RedFlash
========

Why?
----

When running production systems you want to be alerted the moment key events
occur, be they failures or notifications of notable occurences.

Many systems provide the ability to hook into notification services such as
SMS gateways, but one can easily end up putting gateway credentials and user
contact details (telephone numbers) into many independent systems. This makes
adding and changing users cumbersom and complicates temmporarily switching off
alerts to given users.

When you have Nagios, Zabbix, and a dozen services running, all of which want to
alert you, the challenge is large and therefore alerting tends to be done only
for certain systems.

SaaS services do exist to solve this problem by providing an alerting aggregator. Services
such as Alert Grid (http://alert-grid.com) do exactly what is needed: provide one place
for any service to call to issue an alert, and one place to specify who should
get notified. De-coupling the process of raising an alert from who should get it and
how is perfect, and the system works well, though it comes at a cost and with a number
of features I didn't need.

What?
-----

RedFlash de-couples raising an alert from sending. It provides for defining:

- contacts
- groups (of contacts)
- events

A contact is typically a person and, currently, they can have phone numbers, email addresses and twitter handles
associated with them. By logging into the admin you can selectively, at any time, choose to 
enable or disable any of these notification channels on a per-contact basis.

A group represents a named set of contacts. Systems can be configured to notify a group, and
RedFlash will deal with notifying all contacts via all enabled channels.

An event has contacts and/or groups associated with it. When an event is raised by a system a pre-canned
message is sent to all associated recipients. The message can be templated in the admin so that if 
ancilliary arguments are ``POST``ed with the request, those values can be used to construct the 
message.

Redflash? Really?
------------------

Those of you familiar with the BBC series 'Spooks' may recall that when the proverbial hits the 
national security fan in a big way the team get 'redflashed' and across the capital MI5 operatives' 
phones go beep. Whilst not engaged in national security emergencies, a RedFlashing is 
occasionaly useful to those with more mundane website management issues and this is my solution.


Todo
----

- Much better documentation 
- Logging - I was lazy, lazy, lazy. There is no excuse, especially as with Django 1.3 we can now just throw logging config into ``settings.py``
- Should we have a status code/message for when any attempt to send a message results in no recipients getting it on account of all being disabled/erroring? 
- Re-factor the gateway
- move clickatel_delivery_status content into the gateway class
- Allow events to have a custom 'sender number' to be attached...
- Little front-end GUI for sending messages manually

Usage
=====

More documentation is to come here, and there are basic installation notes in the ``INSTALL`` file. 
For now you'll have to read the settings.py to find help with getting this running -
it's not difficult however. Once you have a Clickatell or Nexmo (recommended) account you're much of the way there. Twitter is also fairly straight
forward:

- create a twitter account to be the sender of alerts
- use twitter tools described in ``tweet.py`` to generate the appropriate OAuth keys and place in ``/etc/redflash.py``
- ensure that anyone wishing to receive twitter alerts follows the sending account

Twitter can be configured to SMS any direct messages and thus can be used as a cheap and cheerful SMS gateway. Be warned that there can 
be a considerable delay between the sending of a tweet and the sending of the associated SMS (many, many minutes) so 
this should not be used as a production solution for SMS.

Clients simply call on the RESTful(ish) API sketched out below. If you have Clickatel or Nexmo sending confirmation receipts, it should
be configured to call the ``/ack`` URL. 

An example Python client library can be installed from git://github.com/aquamatt/rfclient.git.
It is packaged with distutils. ``pip install`` it and then::

    from rfclient.redflash import RedFlashClient
    rfc = RedFlashClient(rf_url="http://my.redflash.url", api_key="<key obtained from admin>")
    rfc.notify_contact(<contact_slug>, "message to send")
    rfc.notify_group(<group_slug>, "message to send")

    # args are a set of keyword arguments that get passed to the message
    # template
    rfc.fire_event(<event_slug>, **args)

Synchronous vs Asynchronous sending
===================================

Sending a tweet is a slow process, and even sending an SMS might be slow. The Redflash client doesn't need to hang around waiting for this to happen so we use Celery to distribute the work of transmitting messages and ensure we can return immediately to the client.

You can force synchronous behaviour be setting ``SEND_IN_PROCESS`` True in ``settings.py``. Leave False for best behaviour, though this does require Redis or RabbitMQ to be running. You also need to start at least one celery daemon::

    python manage.py celeryd -E -linfo

Notification channels
=====================

RedFlash can notify via:

- SMS (via a gateway such as Clickatel or Nexmo)
- Email
- Twitter (DM is sent; the user must follow the account from which RedFlash tweets)
- Webhook

Webhooks
--------

To supply a webhook, you must set a service to receive requests at the URL specified. For example::

  http://my.hooks/redflash/

as a base URL would receive updates POSTed to::

  http://my.hooks/redflash/<notification ID>

with POST arguments 'notification_id' and 'message'


You must respond with a 201 (200 accepted though) if the response has been accepted; a 500 if there was an error.

URL API structure
=================

*TODO* Write decent documentation here. For now, these are my notes.

Sending a message
-----------------
POST content:

- api_key
- message

URI:

- /contact/<slug>
- /group/<slug>

Status codes:

- Status 403 if API key forbidden/invalid
- Status 404 if user/group not known or disabled
- Status 201 if message sent
- Status 202 if message sent to some but not all contacts in a group
- Status 500 if message could not be sent due to error or empty message

Firing event
------------
POST content:

- api_key
- n arbitrary keys to be included in message template context

URI:

- /event/<slug>

Status codes:

- Status 403 if API key forbidden/invalid
- Status 404 if event not known or disabled
- Status 201 if event fired
- Status 500 if message could not be sent due to error or empty message

Getting contact/group info
--------------------------

- GET request to URI as above
- API Key passed as get arg
- Key must be enabled for getting data for contacts

Status codes:

- Status 500 if exception raised
- Status 404 if user/group not  known or disabled
- Status 403 if API key forbidden/invalid
- Status 200 if OK

PUT/DELETE requests:

Respond with 403 invalid


Notes on gateways
=================

Some quick notes on gateways other than Nexmo and Clickatell:

- TMC (www.tmcsms.com - looks like cheap virtual numbers, but API is SOAP and
   outbound not so cheap with _from_ 5.9p / msg)
- MessageMedia. Also appear to be SOAP only. Replies flagged to match outbound messages
   which is nice - clickatell can't do that. Pricing not published.
- www.bulksms.co.uk - two-way SMS without needing virtual number. Pricing more expensive
   than clickatell and nexmo
- www.routomessaging.com - seems to be OK pricing. Not sure you get delivery
   receipts.

At the moment we recommend Nexmo highly for the features, the pricing and the straight-forward
global delivery. It is the most recently tested SMS gateway for RedFlash.

Acknowledgements
================

Thanks to James Cranwell-Ward (@jcranwellward) for suggesting the Webhooks
feature - an inspired addition to this tool!
