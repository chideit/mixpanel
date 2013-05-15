mixpanel
========

Python API wrapper for mixpanel

### Sample Usage:


**Initializing:**

	from mixpanel import MP
	mixpanel = MP('MyToken', api_key='MyKey', api_secret='MySecret')
	mixpanel.identify(user.id)

**Tracking an event:**

	mixpanel.track("Signup", {"Plan": "Free"})

**Creating a profile:**

	mixpanel.set({
		'$email': user.email,
		'$username': user.username,
		'$first_name': user.first_name,
		'$last_name': user.last_name,
		'$created': user.date_joined,
		'$last_login': user.last_login,
		'$plan': user.current_plan,
		'lifetime_value': user.amount_paid()
	})

**Importing previous events (need to provide api key upon initializing, and also provide a time):**

	for user in User.objects.all():
		mixpanel.track_import("Signup", {"Plan": "Free"}, time=user.date_joined)
		for payment in user.payment_set.filter(status__in=["SIGNUP", "CANCELLATION"]):
			mixpanel.track_import('Plan Cancelled' if payment.status == 'CANCELLATION' else 'Plan Upgraded', {'Plan': payment.for_package.name}, time=payment.payment_date)
		
		for payment in user.payment_set.filter(status__in=["Completed", "Refunded"]):
			if payment.for_package:
				mixpanel.track_import('Billed' if payment.amount > 0 else 'Refunded', {'Plan': payment.for_package.name, 'Amount': payment.amount}, time=payment.payment_date)
				mixpanel.track_charge(payment.amount, {'Plan': payment.for_package.name}, time=payment.payment_date)
