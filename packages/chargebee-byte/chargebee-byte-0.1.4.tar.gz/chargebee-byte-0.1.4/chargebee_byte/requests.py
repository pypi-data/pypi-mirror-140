from chargebee_byte.parameters import generate_sorting_parameters, generate_equals_parameters, \
    generate_comparison_parameters, generate_collection_parameters, generate_date_parameters, \
    generate_parameters


class ChargebeeRequest(object):
    path = None

    def __init__(self, parameters=None):
        parameters = parameters or {}

        self.allowed_parameters = self.generate_allowed_parameters()
        self.check_parameters(parameters)
        self.data = parameters

    def generate_allowed_parameters(self):
        raise NotImplementedError()

    def check_parameters(self, parameters):
        incorrect_parameters = set(parameters.keys()) - set(self.allowed_parameters)
        if incorrect_parameters:
            raise ValueError('The following parameters are not allowed: {}'
                             .format(', '.join(incorrect_parameters)))


class SubscriptionRequest(ChargebeeRequest):
    path = '/subscriptions'

    def generate_allowed_parameters(self):
        params = generate_equals_parameters([
            'status', 'cancel_reason', 'id', 'customer_id', 'plan_id', 'remaining_billing_cycles'])
        params += generate_date_parameters([
            'created_at', 'activated_at', 'next_billing_at', 'cancelled_at', 'updated_at'])
        params += generate_parameters([
            'remaining_billing_cycles', 'activated_at', 'cancel_reason'], ['is_present'])
        params += generate_collection_parameters([
            'status', 'cancel_reason', 'id', 'customer_id', 'plan_id'])

        params += generate_sorting_parameters(['sort_by'])
        params += generate_parameters(['has_scheduled_changes'], ['is'])
        params += generate_comparison_parameters(['remaining_billing_cycles'])
        params += generate_parameters(['remaining_billing_cycles'], ['between'])
        params += generate_parameters(['id', 'customer_id', 'plan_id'], ['starts_with'])

        return ['limit', 'offset', 'include_deleted'] + params


class CustomerRequest(ChargebeeRequest):
    path = '/customers'

    def generate_allowed_parameters(self):
        params = generate_equals_parameters(['id', 'first_name', 'last_name', 'email', 'company', 'phone',
                                             'auto_collection', 'taxability'])
        params += generate_date_parameters(['created_at', 'updated_at'])
        params += generate_collection_parameters(['id', 'auto_collection', 'taxability'])
        params += generate_sorting_parameters(['sort_by'])
        params += generate_parameters(['first_name', 'last_name', 'email', 'company', 'phone'],
                                      ['is_present', 'starts_with'])
        params += generate_parameters(['id'], ['starts_with'])

        return ['limit', 'offset', 'include_deleted'] + params


class InvoiceRequest(ChargebeeRequest):
    path = '/invoices'

    def generate_allowed_parameters(self):
        params = generate_sorting_parameters(['sort_by'])
        params += generate_equals_parameters(['id', 'subscription_id', 'customer_id', 'status', 'price_type', 'total',
                                              'amount_paid', 'amount_adjusted', 'credits_applied', 'amount_due',
                                              'dunning_status', 'payment_owner', 'void_reason_code'])
        params += generate_collection_parameters(['id', 'subscription_id', 'customer_id', 'status', 'price_type',
                                                  'dunning_status', 'payment_owner', 'void_reason_code'])
        params += generate_date_parameters(['date', 'paid_at', 'updated_at', 'voided_at'])
        params += generate_comparison_parameters(['total', 'amount_paid', 'amount_adjusted', 'credits_applied',
                                                  'amount_due'])
        params += generate_parameters(['id', 'subscription_id', 'customer_id', 'payment_owner', 'void_reason_code'],
                                      ['starts_with'])
        params += generate_parameters(['subscription_id', 'dunning_status'], ['is_present'])
        params += generate_parameters(['recurring'], ['is'])
        params += generate_parameters(['total', 'amount_paid', 'amount_adjusted', 'credits_applied',
                                       'amount_due'], ['between'])

        return ['limit', 'offset', 'include_deleted'] + params
