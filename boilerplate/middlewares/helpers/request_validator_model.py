from pymodm import EmbeddedMongoModel, MongoModel, fields

from commons.utils.default_model_manager import DefaultManager


class Action(EmbeddedMongoModel):
    actionType = fields.BooleanField(required=True)
    values = fields.MongoBaseField(required=True)

    class Meta:
        final = True


class Params(EmbeddedMongoModel):
    name = fields.CharField(required=True)
    dataType = fields.CharField(required=True)
    regex = fields.CharField(blank=True)
    isRequired = fields.BooleanField()
    action = fields.EmbeddedDocumentField(Action, blank=True)

    class Meta:
        final = True


class RequestValidationConfig(MongoModel):
    '''Mongo model for request validation config.
    '''

    routeName = fields.CharField(required=True)
    method = fields.CharField(required=True)
    isActive = fields.BooleanField(required=True)
    queryParams = fields.EmbeddedDocumentListField(Params, blank=True)
    urlParams = fields.EmbeddedDocumentListField(Params, blank=True)
    requestBodySchema = fields.DictField(blank=True)
    objects = DefaultManager()

    class Meta:
        collection_name = "RequestValidationConfig"
        final = True
