mixpanel
========
Python API wrapper for mixpanel. 
This will allow you to call many of the methods that you can call on mixpanel via the JS API, but from python. 
This does not provide a queueing mechanism to reduce requests. For that, you can use *celery*. 

Depends on the *requests* library.

Based on the specs from the mixpanel docs:
- [Http Specs](https://mixpanel.com/docs/api-documentation/http-specification-insert-data)
- [People Http Specs](https://mixpanel.com/docs/people-analytics/people-http-specification-insert-data)

The following methods are implemented:
- *track* - allows you to perform the standard event tracking.
- *alias* - allows you to create an alias for a user's distinct_id
- *track_import* - the same as *track*, but allows you to specify a historic time parameter. This hits a different endpoint on mixpanel.

People based methods are as follows:
- *set* - sets one or many properties on the user profile.
- *set_once* - sets only the list of properties on the profile that aren't already defined.
- *add* - adds to a numeric property on the user profile (e.g. adding to lifetime_value or num_actions_performed)
- *append* - appends an item to a list property on the user profile.
- *track_charge* - convenience method which appends a charge to the profile's list of charges (for revenue tracking).
- *clear_charges* - convenience method which sets the transaction list to []
- *delete_user* - removes the user profile

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
