from marshmallow import (
    Schema,
    fields,
    validate,
)


class AmountLicensingCollabResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    licensing_collab_id = fields.Integer(required=True)
    value = fields.Decimal(required=True)
    type = fields.String(required=True)
    updated_at = fields.DateTime()
