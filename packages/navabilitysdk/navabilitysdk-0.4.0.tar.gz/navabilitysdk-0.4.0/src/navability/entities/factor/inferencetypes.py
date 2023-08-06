from dataclasses import dataclass

import numpy as np
from marshmallow import Schema, fields, post_load

from navability.entities.factor.distributions import Distribution


@dataclass
class InferenceType:
    """
    Base type for all factor classes.
    """

    pass


@dataclass
class PriorPose2(InferenceType):
    Z: Distribution

    def __repr__(self):
        return f"<{self.__class__.__name__}(Z={str(self.Z)})>"

    def dump(self):
        return PriorPose2Schema().dump(self)

    def dumps(self):
        return PriorPose2Schema().dumps(self)

    # TODO: Deserializing this.


class PriorPose2Schema(Schema):
    Z = fields.Method("get_Z", "set_Z", required=True)

    class Meta:
        ordered = True

    def get_Z(self, obj):
        return obj.Z.dump()

    def set_Z(self, obj):
        raise Exception("This has not been implemented yet.")

    # @post_load
    # def load(self, data, **kwargs):
    #     return PriorPose2(**data)


@dataclass
class Pose2Pose2(InferenceType):
    Z: Distribution

    def __repr__(self):
        return f"<{self.__class__.__name__}(Z={str(self.Z)})>"

    def dump(self):
        return Pose2Pose2Schema().dump(self)

    def dumps(self):
        return Pose2Pose2Schema().dumps(self)

    # TODO: Deserializing this.


class Pose2Pose2Schema(Schema):
    Z = fields.Method("get_Z", "set_Z", required=True)

    def get_Z(self, obj):
        return obj.Z.dump()

    def set_Z(self, obj):
        raise Exception("This has not been implemented yet.")

    @post_load
    def marshal(self, data, **kwargs):
        return PriorPose2(**data)


@dataclass
class Pose2AprilTag4Corners(InferenceType):
    corners: np.ndarray
    homography: np.ndarray
    K: np.ndarray
    taglength: float
    id: int
    _type: str = "/application/JuliaLang/PackedPose2AprilTag4Corners"

    def dump(self):
        return Pose2AprilTag4CornersSchema().dump(self)

    def dumps(self):
        return Pose2AprilTag4CornersSchema().dumps(self)

    # TODO: Deserializing this.


class Pose2AprilTag4CornersSchema(Schema):
    corners = fields.List(fields.Float, required=True)
    homography = fields.List(fields.Float, required=True)
    K = fields.List(fields.Float, required=True)
    taglength = fields.Float(required=True)
    id = fields.Int(required=True)
    _type = fields.String(default="/application/JuliaLang/PackedPose2AprilTag4Corners")

    class Meta:
        ordered = True

    @post_load
    def marshal(self, data, **kwargs):
        return Pose2AprilTag4Corners(**data)
