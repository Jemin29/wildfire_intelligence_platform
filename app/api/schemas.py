from __future__ import annotations

from marshmallow import Schema, fields, validate


class PredictionRequestSchema(Schema):
    temperature = fields.Float(required=True)
    humidity = fields.Float(required=True)
    rainfall = fields.Float(required=True)
    wind_speed = fields.Float(required=True)
    vegetation = fields.Float(required=True)
    soil_moisture = fields.Float(required=True)
    include_explainability = fields.Boolean(load_default=False)
    lat = fields.Float(load_default=None)
    lon = fields.Float(load_default=None)
    request_id = fields.String(load_default=None)


class WeatherQuerySchema(Schema):
    lat = fields.Float(required=True)
    lon = fields.Float(required=True)


class AlertTriggerSchema(Schema):
    risk_score = fields.Float(required=True)
    location = fields.String(required=True, validate=validate.Length(min=1))
    message = fields.String(load_default="")
    source = fields.String(load_default="prediction")
    prediction_id = fields.Integer(load_default=None)
    user_id = fields.Integer(load_default=None)


class LookbackQuerySchema(Schema):
    days = fields.Integer(load_default=30)


class HorizonQuerySchema(Schema):
    horizon = fields.Integer(load_default=7)


class YearsQuerySchema(Schema):
    years = fields.Integer(load_default=5)
