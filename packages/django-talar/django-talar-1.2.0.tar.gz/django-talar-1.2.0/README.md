# django-talar
Django app for [Talar](https://talar.app) service.

## Installation
1. `pip install django-talar`.
2. Add `django_talar` to your django settings `INSTALLED_APPS`.
3. Modify code below and also insert it into django settings:

    ```python
        TALAR = {
            'project_id': env.str('TALAR_PROJECT_ID', None),
            'key_id': env.str('TALAR_KEY_ID', None),
            'key_secret': env.str('TALAR_KEY_SECRET', None),
        }
    ```

4. Include this into your core urls:

    ```python
        path('talar/', include(('django_talar.urls', 'talar'))),
    ```

## Basic usage
django-talar contains basic form `django_talar.forms.PaymentForm` and template
`django_talar/talar_make_payment.html` for making payments. It is suggested to
use it by adding your own view like so:

```python
def make_payment(request):
    data = {
        'external_id': EXTERNAL_ID, # You order/payment unique key that will be used to identify payment
        'amount': AMOUNT, # your data
        'currency': CURRENCY, # your data
        'continue_url': CONTINUE_URL, # Insert address for redirection after successfull payment
    }

    talar = Talar(
       settings.TALAR['project_id'],
       settings.TALAR['key_id'],
       settings.TALAR['key_secret']
    )
    url = talar.url
    data = talar.create_payment_data(data)

    payment_form = PaymentForm(data={
        'key_id': talar.access_key_id,
        'encrypted': data
    })

    return render(request, 'django_talar/make_payment.html', {
        'url': url,
        'payment_form': payment_form
    })
```

html code will handle redirection if everything is correct:

```html
    <div>
        <p>{% trans 'After continuing you will be redirected to payment provider site.' %}</p>
        <form action="{{ url }}" method="post" class="form-inline">
            {{ payment_form.as_p }}
            <button type=submit class="btn btn-primary">{% trans 'Pay' %}</button>
        </form>
    </div>
```
