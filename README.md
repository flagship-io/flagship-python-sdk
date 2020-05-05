---
title: Flagship SDK documentation
weight: 1
language_tabs:
- python
---

# Introduction to Python SDK

Welcome to the Flagship Python SDK documentation!

The following documentation helps you to run Flagship on your python server/script.

The sdk helps you :

 - Set a visitor id
 - Update visitor context
 - Allocate campaigns from the decision API
 - Get modifications
 - Activate campaigns
 - Send events

Feel free to [contact us](mailto:product@abtastycom) if you have any questions regarding this documentation.

# Getting started

Follow these steps to install and run your script with the Flagship library.

## Prerequisites

* Your server/device must run python version 2.7.18 minimum.
* Your server/device must have an access to the internet.
* You need the pip package installer in your python environment.

## Install the library

Our python SDK is available on <a href="https://pypi.org/">pypi.org</a>. To install it, simply run the following command in your python environement in a terminal:


**`pip install flagship`**


Either you can install the libray from the sources by running this command:

**`pip install path_to_flagship_repository`**


Replace *path_to_flagship_repository* by the path of the directory from the cloned repository.
<br><br>

<aside class="notice">
If you have installed the libray from its sources, its dependencies should have been installed automatically. If it is not the case execute the following command in your python env: 
<br><br><b><code>
pip install -r requirements.txt
</code></b><br><br>
</aside>


## Import and initialize the library

```python
from flagship.app import Flagship
from flagship.config import Config


Flagship.instance().start(Config("your_env_id", "your_api_key"))
```

Once the libray is installed in your python environement, in your python source file : 
- First import the **Flagship**, **Config** class from **flagship.app** and **flagship.config**.<br>
- Get the Flagship install by calling **Flagship.instance()**. <br>
- Then call the **start()** function passing a **Config** object as parameter.


<aside class="notice">
You can find your Flagship environment id in the parameters\integration section of your Flagship account. (Check <a href="https://developers.flagship.io/getting_started">Getting Started</a>)
</aside>

<br><br>

### Configuration

```python
from flagship.app import Flagship
from flagship.config import Config
from flagship.handler import FlagshipEventHandler

class CustomEventHandler(FlagshipEventHandler):
    def __init__(self):
        FlagshipEventHandler.__init__(self)

    def on_log(self, level, message):
        print("Log >> " + message)
        pass

    def on_exception_raised(self, exception, traceback):
        FlagshipEventHandler.on_exception_raised(self, exception, traceback)
        print("Exception >> " + str(exception))
        pass


 Flagship.instance().start(
        Config("your_env_id", "your_api_key", event_handler=CustomEventHandler())
```

The **Config** class helps you to configure the SDK.

**`Config.__init__(self, env_id, api_key="", **kwargs):`**

Parameter | Type | Description
--------- | ------- | -----------
env_id | str | Environment id provided by Flagship.
api_key | str | (optional) Api authentication key provided by Flagship.
**kwargs | | (optional)
event_handler | FlagshipEventHandler | custom FlagshipEventHandler implementation to provide for log and error handling.


<br>


# Create a visitor

## Create a visitor with an ID and a Context

```python

context = {
	'isVipUser':True,
	'name':'visitor',
	'age':30
}

visitor = Flagship.instance().create_visitor("user_#1234", context)
```

The visitor instance is an helper object which helps you to manage context and campaigns for a visitor identified by a unique ID.

The visitor context is a property dataset which defines the current user of your app. This dataset is sent and used
by the Flagship decision API as targeting for campaign allocation. For example, you could pass a VIP status in the context and
then the decision API would enable or disable a specific feature flag.

<aside class="notice">Visitor context values are used for campaign targeting configuration.</aside>

<br>

To create a visitor use the function **`create_visitor()'**.

<br>

**`def create_visitor(self, visitor_id, context={})`**

<br>

Parameter | Type | Description
--------- | ------- | -----------
visitor_id | str | ID of the visitor (must be unique for a visitor).
context | dict | (optional) dictionnary of visitor properties (key, values).

<aside class="warning">
Visitor context keys type must be: str</br>
Visitor context values type must be: str, bool, int, float</br>
</aside>

## Updating the visitor Context

```python

context = {
	'isVipUser':True,
	'name':'visitor',
	'age':30
}

visitor = Flagship.instance().create_visitor("user_#1234")

visitor.update_context(context)
visitor.update_context(('age', 31), True)
```

The visitor context can be updated at anytime whenever a property of your current visitor has changed.

The following method from the visitor instance allows you to set new context values matching the given keys.

<br>

**`def update_context(self, context, synchronize=False)`**

<br>

Parameter | Type | Description
--------- | ------- | -----------
context | dict or tuple | Add a tuple (key, value) or a dictionary {key: value}.
synchronize | bool | synchronize: (optional : false by default) If set to True, it will automatically call synchronize_modifications() and then update the modifications from the server for all campaigns according to the updated current visitor context. You can also update it manually later with: synchronize_modifications().

<br>

<aside class="warning">
Visitor context keys type must be: str</br>
Visitor context values type must be: str, bool, int, float</br>
</aside>

# Campaign integration

## Synchronizing campaigns

```python
visitor = Flagship.instance().create_visitor("user_#1234", {'isVip':True})

#Synchronize by passing True to update context.
visitor.update_context(('age', 31), True)

#Synchronize with stand alone function
visitor.synchronize_modifications()
```


Synchronizing campaign modifications allows you to automatically call the Flagship decision API, which makes the allocation according to user context and gets all their modifications.

All the applicable modifications are stored in the SDK and are updated asynchronously when `synchronizeModifications()` is called.

Simply call the method **synchronize_modifications()** from the visitor instance. It's also possible to synchronize campaigns by passing True to the function **update_context** as synchronize parameter.

<br>

**`def synchronize_modifications(self)`**

<br>

## Retrieving modifications

```python
visitor = Flagship.instance().create_visitor("user_#1234", {'isVip':True})
visitor.synchronize_modifications()

vip_feature_enabled = visitor.get_modification('vip_feature', False)
```

Once the campaigns have been **allocated** and **synchronized** all the modifications are stored in the SDK. Then, you can retrieve them with the following functions from the visitor instance:


<br>

**`def get_modification(self, key, default_value, activate=False)`**

<br>


Parameter | Type | Description
--------- | ------- | -----------
key | str | key associated to the modification.
default_value | int, bool, float, str | default value returned when the key does not match any modification value.
activate | bool | (optional) false by default Set this parameter to true to automatically report on our server that the current visitor has seen this modification. If false, call the activate_modification() later.
-----|-----|----- 
return | int, bool, float, str | current modification or default value.


<br>

## Activating modifications

```python
visitor = Flagship.instance().create_visitor("user_#1234", {'isVip':True})
visitor.synchronize_modifications()

#Activation during get_modification
vip_feature_enabled = visitor.get_modification('vip_feature', True)

#Activation from stand alone activate_modification
menu_order = visitor.get_modification('menu_order', False)
visitor.activate_modification('menu_order')

```

Once a modification has been printed on the screen for a user, you must send an activation event to tell Flagship that the user has seen this specific variation.
It is possible to activate a modification eighter passing True to **get_modification()** as **activate** paramater or by using the following **activate_modification()** method from the visitor instance.

<br>

**`def activate_modification(self, key)`**

<br>

Parameter | Type | Description
--------- | ------- | -----------
key | String | key which identifies the modification

# Hit Tracking

This section helps send tracking and learn how to build hits in order to aprove campaign goals.

The different types of Hits are:

* Page
* Transaction
* Item
* Event

**They must all be built and sent with the following function from the visitor instance:**

**`def send_hit(self, hit)`**

## Page

```python
visitor.send_hit(Page("views.py"))
```

This hit should be sent each time a visitor arrives on a new interface.

<br>

**`Page.__init__(self, origin):`**

<br>

Builder Parameter | Type | Required | Description
--------- | ------- | ----------- | -----------
origin | String | Yes | uri / interface name / script name

<aside class="notice">The <code>Page</code> hit isn't available yet in the Flagship reporting view.</aside>

## Transaction

```python
visitor.send_hit(Transaction("#309830", "purchases")
                     .with_currency("EUR")
                     .with_item_count(3)
                     .with_payment_method("cb")
                     .with_shipping_cost(4.99)
                     .with_shipping_method("1d")
                     .with_taxes(9.99)
                     .with_total_revenue(420.00)
                     .with_coupon_code("#SAVE10"))
```

This hit should be sent when a user complete a Transaction.

<br>

**`Transaction.__init__(self, transaction_id, affiliation)`**

<br>

Builder Parameter | Type | Required | Description
--------- | ------- | ----------- | ----------
transactionId | String | Yes | Transaction unique identifier.
affiliation | String | Yes | Transaction name. Name of the goal in the reporting.

<br>

Methods are provided to set the following values: 

<br>

Builder Parameter | Type | Required | Description
--------- | ------- | ----------- | ----------
totalRevenue | Float | No | Total revenue associated with the transaction. This value should include any shipping or tax costs.
shippingCost | Float | No | Specifies the total shipping cost of the transaction.
withShippingMethod | String | No | Specifies the shipping method of the transaction.
taxes | Float | No | Specifies the total taxes of the transaction.
currency | String | No | Specifies the currency used for all transaction currency values. Value should be a valid ISO 4217 currency code.
paymentMethod | String | No | Specifies the payment method for the transaction.
itemCount | Int | No | Specifies the number of items for the transaction.
couponCode | String | No | Specifies the coupon code used by the customer for the transaction.

## Item

```python
visitor.send_hit(Item("#309830", "ATX2080")
                     .with_item_category("hardware")
                     .with_item_code("cg_atx_20802020")
                     .with_item_quantity(2)
                     .with_price(210.00))
```

This hit is linked to a transaction. It must be send after the corresponding transaction.

<br>

**`Item.__init__(self, transaction_id, product_name)`**

<br>

Builder Parameter | Type | Required | Description
--------- | ------- | ----------- | -------
transactionId | String | Yes | Transaction unique identifier.
product name | String | Yes | Product name.

<br>

Methods are provided to set the following values: 

<br>

Builder Parameter | Type | Required | Description
--------- | ------- | ----------- | -------
price | Float | No | Specifies the item price.
itemCode | String | No | Specifies the item code or SKU.
itemCategory | String | No | Specifies the item category.
itemQuantity | Int | No | Specifies the item quantity


## Event

```python
visitor.send_hit(Event(EventCategory.USER_ENGAGEMENT, "click_basket")
                     .with_event_label('basket button')
                     .with_event_value(420))
```

This hit can be anything you want: for example a click or a newsletter subscription.

<br>

**`Event.__init__(self, category, action)`**

<br>


Builder Parameter | Type | Required | Description
--------- | ------- | ----------- | ------
category | EventCategory | Yes |  category of the event (ACTION_TRACKING or USER_ENGAGEMENT).
action | String | Yes | the event action.

<br>

Methods are provided to set the following values: 

<br>

Builder Parameter | Type | Required | Description
--------- | ------- | ----------- | ------
label | String | No | label of the event.
value | Number | No | Specifies a value for this event. must be non-negative.

## Common parameters for hits

```python
visitor.send_hit(Page("script.py")
                            .with_ip("133.3.223.1")
                            .with_locale("fr-fr")
                            .with_resolution(640, 480)
                            .with_session_number(3))
```

<br>

Parameter | Type | Description
--------- | ------- | -----------
userIp | String | **optional** User IP
screenResolution | String | **optional** Screen Resolution.
userLanguage | String | **optional**  User Language
currentSessionTimeStamp | Int64 | **optional** Current Session Timestamp
sessionNumber | Int | **optional** Session Number

# Sources

Sources of the library SDK are available at :
https://github.com/abtasty/flagship-python-sdk


