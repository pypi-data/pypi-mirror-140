from .init_creds import init_mongo

import mercadopago

db = init_mongo()


def get_payment(payment_id, sdk):
    response = sdk.payment().search(filters={"id": payment_id})
    return response["response"]


def get_merchant_from_payment(payment_id: str):
    """ Obtener el merchant a partir de un pago de mercadopago

          :param payment_id: id del pago
          :type payment_id: str
          :return: el merchant del pago
          :rtype: ObjectId
          """
    for merchant in db.merchants.find({}):
        try:
            sdk = mercadopago.SDK(merchant["keys"]["access_token"])
        except KeyError:
            continue
        payment = get_payment(payment_id, sdk)
        if "results" in payment.keys():
            if payment["results"]:
                return merchant["_id"]


def get_sdk_from_payment(payment_id: str):
    """ Obtener el sdk a partir de un pago de mercadopago

      :param payment_id: id del pago
      :type payment_id: str
      :return: el sdk ya instanciado de mercadopago
      :rtype: mercadopago.SDK
      """
    for merchant in db.merchants.find({}):
        try:
            sdk = mercadopago.SDK(merchant["keys"]["access_token"])
        except KeyError:
            continue
        payment = get_payment(payment_id, sdk)
        if "results" in payment.keys():
            if payment["results"]:
                return sdk

