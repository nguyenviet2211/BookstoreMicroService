"""
Saga Orchestrator for Order Creation.
Implements the Saga pattern for distributed transactions:
1. Create order (Pending)
2. Reserve payment
3. Reserve shipping
4. Confirm order
5. Compensate if failure
"""
import requests
import logging
from django.conf import settings
from .models import Order, SagaLog

logger = logging.getLogger(__name__)


class OrderSagaOrchestrator:
    def __init__(self, order):
        self.order = order

    def _log_step(self, step, status, details=""):
        SagaLog.objects.create(
            order=self.order, step=step, status=status, details=details
        )

    def execute(self):
        """Execute the Saga steps sequentially."""
        try:
            # Step 1: Order already created with 'pending' status
            self._log_step("create_order", "success", f"Order #{self.order.id} created")

            # Step 2: Reserve payment
            if not self._reserve_payment():
                self._compensate("payment_failed")
                return False

            # Step 3: Reserve shipping
            if not self._reserve_shipping():
                self._compensate("shipping_failed")
                return False

            # Step 4: Confirm order
            self.order.status = 'confirmed'
            self.order.save()
            self._log_step("confirm_order", "success", "Order confirmed")

            return True

        except Exception as e:
            logger.error(f"Saga failed for order #{self.order.id}: {e}")
            self._compensate("unexpected_error")
            return False

    def _reserve_payment(self):
        """Step 2: Call pay-service to reserve payment."""
        try:
            response = requests.post(
                f"{settings.PAY_SERVICE_URL}/api/payments/reserve/",
                json={
                    "order_id": self.order.id,
                    "customer_id": self.order.customer_id,
                    "amount": str(self.order.total_amount),
                    "method": self.order.payment_method,
                },
                timeout=10
            )
            if response.status_code == 201:
                self.order.status = 'payment_reserved'
                self.order.save()
                self._log_step("reserve_payment", "success")
                return True
            else:
                self._log_step("reserve_payment", "failed", response.text)
                return False
        except requests.exceptions.RequestException as e:
            self._log_step("reserve_payment", "failed", str(e))
            return False

    def _reserve_shipping(self):
        """Step 3: Call ship-service to reserve shipping."""
        try:
            response = requests.post(
                f"{settings.SHIP_SERVICE_URL}/api/shipments/reserve/",
                json={
                    "order_id": self.order.id,
                    "customer_id": self.order.customer_id,
                    "address": self.order.shipping_address,
                    "method": self.order.shipping_method,
                },
                timeout=10
            )
            if response.status_code == 201:
                self.order.status = 'shipping_reserved'
                self.order.save()
                self._log_step("reserve_shipping", "success")
                return True
            else:
                self._log_step("reserve_shipping", "failed", response.text)
                return False
        except requests.exceptions.RequestException as e:
            self._log_step("reserve_shipping", "failed", str(e))
            return False

    def _compensate(self, reason):
        """Compensating transactions - rollback on failure."""
        logger.warning(f"Compensating order #{self.order.id}: {reason}")
        self.order.status = 'cancelled'
        self.order.save()

        # Cancel payment if reserved
        if reason in ("shipping_failed", "unexpected_error"):
            try:
                requests.post(
                    f"{settings.PAY_SERVICE_URL}/api/payments/cancel/",
                    json={"order_id": self.order.id},
                    timeout=10
                )
                self._log_step("compensate_payment", "compensated")
            except requests.exceptions.RequestException as e:
                self._log_step("compensate_payment", "failed", str(e))

        # Cancel shipping if reserved
        if reason == "unexpected_error":
            try:
                requests.post(
                    f"{settings.SHIP_SERVICE_URL}/api/shipments/cancel/",
                    json={"order_id": self.order.id},
                    timeout=10
                )
                self._log_step("compensate_shipping", "compensated")
            except requests.exceptions.RequestException as e:
                self._log_step("compensate_shipping", "failed", str(e))

        self._log_step("saga_compensated", "compensated", reason)
