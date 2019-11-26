"""
Attachment model.

Attributes:
    Dimensions: namedtuple that conveniently encodes the width, height, and
        allow_crop flag to identify a specific Derivative.
    EXIF_Field: namedtuple to store the key/description/value/extra data of a
        single piece of EXIF data.
    EXIF_CATEGORIES: Mapping of EXIF category names and the candidate fields
        within each. This serves a few purposes: it is a whitelist that only
        permits safe/relevant fields to be displayed; it groups fields in a
        slightly more manageable way; it defines the display order in contexts
        where display order matters; and in some cases it specifies a succession
        of fields names that should be tried in order until data is located.
    logger: Logger instance scoped to the current module name.
"""

import logging
from collections import namedtuple
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.collections import column_mapped_collection
from windowbox.database import db
from windowbox.models import FilesystemMixin
from windowbox.models.post import Post

Dimensions = namedtuple('Dimensions', ['width', 'height', 'allow_crop'])
EXIF_Field = namedtuple('EXIF_Field', ['attribute', 'description', 'value', 'raw_value'])

EXIF_CATEGORIES = {
    'camera': [
        ['EXIF:FocalLength'],
        ['EXIF:FocalLengthIn35mmFormat'],
        ['Composite:ScaleFactor35efl'],
        ['EXIF:DigitalZoomRatio'],
        ['Composite:ShutterSpeed', 'EXIF:ShutterSpeedValue'],
        ['EXIF:ApertureValue'],
        ['EXIF:ISO'],
        ['EXIF:Flash'],
        ['EXIF:WhiteBalance'],
        ['EXIF:MeteringMode'],
        ['EXIF:ExposureMode'],
        ['EXIF:ExposureProgram'],
        ['EXIF:ExposureTime'],
        ['EXIF:FNumber'],
        ['Composite:CircleOfConfusion'],
        ['Composite:FOV'],
        ['Composite:HyperfocalDistance'],
        ['EXIF:BrightnessValue'],
        ['Composite:LightValue']],
    'image': [
        ['PNG:ImageWidth', 'EXIF:ExifImageWidth', 'File:ImageWidth'],
        ['PNG:ImageHeight', 'EXIF:ExifImageHeight', 'File:ImageHeight'],
        ['EXIF:Orientation'],
        ['EXIF:XResolution', 'JFIF:XResolution'],
        ['EXIF:YResolution', 'JFIF:YResolution'],
        ['EXIF:ResolutionUnit', 'JFIF:ResolutionUnit'],
        ['MakerNotes:HDRImageType'],
        ['EXIF:Gamma'],
        ['EXIF:Sharpness'],
        ['EXIF:SensingMethod'],
        ['EXIF:SceneType'],
        ['EXIF:SceneCaptureType'],
        ['EXIF:SubjectArea'],
        ['EXIF:SubjectDistanceRange'],
        ['PNG:Filter'],
        ['PNG:Interlace'],
        ['PNG:BitDepth', 'File:BitsPerSample'],
        ['PNG:ColorType', 'EXIF:ColorSpace'],
        ['File:ColorComponents'],
        ['EXIF:ComponentsConfiguration'],
        ['EXIF:YCbCrPositioning'],
        ['File:YCbCrSubSampling'],
        ['File:FileType'],
        ['File:FileSize'],
        ['PNG:Compression', 'EXIF:Compression'],
        ['File:EncodingProcess'],
        ['File:ExifByteOrder']],
    'environment': [
        ['EXIF:Software'],
        ['EXIF:ExifVersion'],
        ['EXIF:FlashpixVersion'],
        ['JFIF:JFIFVersion'],
        ['XMP:XMPToolkit'],
        ['EXIF:InteropVersion'],
        ['EXIF:InteropIndex'],
        ['Composite:RunTimeSincePowerUp']],
    'hardware': [
        ['EXIF:Make'],
        ['EXIF:Model'],
        ['EXIF:LensMake'],
        ['EXIF:LensModel'],
        ['EXIF:LensInfo']]}

logger = logging.getLogger(__name__)


class AttachmentEXIF(db.Model):
    """
    Attachment EXIF data model.

    This is an entity-attribute-value table containing arbitrary EXIF data for
    each Attachment. There are no guarantees about the schema or the presence/
    format of individual elements here -- anything important should be a scalar
    column of the Attachment itself.

    Attributes:
        NAME_LENGTH: The maximum size of the name column.
        VALUE_LENGTH: The maximum size of the value column.
    """

    NAME_LENGTH = 64
    VALUE_LENGTH = 255

    __tablename__ = 'attachment_exif'
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    attachment_id = db.Column(
        db.Integer, db.ForeignKey('attachment.id', ondelete='CASCADE'),
        nullable=False, index=True)
    attribute = db.Column(db.Unicode(length=NAME_LENGTH), nullable=False)
    value = db.Column(db.Unicode(length=VALUE_LENGTH), nullable=False)


class Attachment(db.Model, FilesystemMixin):
    """
    Attachment model.

    An Attachment is analogous to a single attachment of an email message. Each
    Attachment belongs to one Post and references data in one file.

    Attributes:
        MIME_TYPE_LENGTH: The maximum size of the mime_type column.
        GEO_ADDRESS_LENGTH: The maximum size of the geo_address column.
        CROP_FLAG_ALLOW: Character to use in Derivative URLs to indicate the
            client is willing to receive a cropped version of the original
            image.
        CROP_FLAG_DISALLOW: Character to use in Derivative URLs to indicate the
            client is unwilling to received cropped images, and instead wants
            the width or height to be adjusted down to return the full image in
            the original aspect ratio.
        CANNED_DIMENSIONS_MAP: Mapping of human names to fixed width/height/crop
            values. Provides a more convenient and meaningful "handle" to a
            given image size rather than using hard-coded pixel values.
    """

    MIME_TYPE_LENGTH = 255
    GEO_ADDRESS_LENGTH = 255
    CROP_FLAG_ALLOW = 'x'
    CROP_FLAG_DISALLOW = '~'
    CANNED_DIMENSIONS_MAP = {
        'full': Dimensions(width=None, height=None, allow_crop=False),
        'opengraph': Dimensions(width=750, height=750, allow_crop=False),
        'single': Dimensions(width=960, height=720, allow_crop=False),
        'single2x': Dimensions(width=1920, height=1440, allow_crop=False),
        'thumbnail': Dimensions(width=300, height=300, allow_crop=True),
        'thumbnail2x': Dimensions(width=600, height=600, allow_crop=True)}

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    post_id = db.Column(
        db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'),
        nullable=False, index=True)
    mime_type = db.Column(db.Unicode(length=MIME_TYPE_LENGTH), nullable=False)
    orientation = db.Column(db.Integer, nullable=True)
    geo_latitude = db.Column(db.DECIMAL(11, 8), nullable=True)
    geo_longitude = db.Column(db.DECIMAL(11, 8), nullable=True)
    geo_address = db.Column(db.Unicode(length=GEO_ADDRESS_LENGTH), nullable=True)

    post = db.relationship(Post, backref=db.backref('attachments', cascade='all, delete-orphan'))

    _exif_data = db.relationship(
        AttachmentEXIF, collection_class=column_mapped_collection(AttachmentEXIF.attribute))
    exif = association_proxy(
        '_exif_data', 'value', creator=lambda a, v: AttachmentEXIF(attribute=a, value=v))

    def new_derivative(self, **kwargs):
        """
        Create a fresh Derivative instance connected to this Attachment.

        Does not require any arguments, however any keyword args that are
        provided will be passed to the Derivative constructor.

        Returns:
            New Derivative instance.
        """
        from windowbox.models.derivative import Derivative

        kwargs['attachment'] = self
        kwargs['mime_type'] = self.mime_type

        return Derivative(**kwargs)

    def populate_exif(self, *, exiftool_client):
        """
        Populate the EXIF dictionary from the current storage data.

        Args:
            exiftool_client: Instance of ExifToolClient configured to read EXIF
                metadata from files.
        """
        self.exif = exiftool_client.read_file(self.storage_path())
        self.orientation = self.exif.get('EXIF:Orientation.num')

    def populate_geo(self, *, gmapi_client):
        """
        Populate the `geo_*` attributes from the current EXIF data.

        If the EXIF data does not have GPS information, this method gracefully
        sets all relevant attributes to None. Otherwise, an attempt is made to
        look up the address via the Google Maps API.

        Args:
            gmapi_client: Instance of GoogleMapsAPIClient configured with a
                valid Google Maps API key.
        """
        self.geo_latitude = None
        self.geo_longitude = None
        self.geo_address = None

        latitude = self.exif.get('Composite:GPSLatitude.num')
        longitude = self.exif.get('Composite:GPSLongitude.num')

        if latitude is not None and longitude is not None:
            logger.debug(f'Attachment ID {self.id} has geo coordinates; parsing')

            self.geo_latitude = float(latitude)
            self.geo_longitude = float(longitude)
            self.geo_address = gmapi_client.latlng_to_address(
                latitude=latitude, longitude=longitude)

    def to_url_kwargs(self, canned_dimensions):
        """
        Reduce this instance, plus the passed canned dimensions, to URL kwargs.

        The return value of this method is designed to be passed to Flask's
        url_for() function. The inverse of this method is in
        AttachmentController.decode_dimensions().

        Args:
            canned_dimensions: String containing one of the dimensions names
                from `CANNED_DIMENSIONS_MAP`.

        Returns:
            Dict of arguments that identify this Attachment as well as the
            identifying information for one of its Derivatives.
        """
        dim_tuple = self.CANNED_DIMENSIONS_MAP[canned_dimensions]

        extension = self.KNOWN_EXTENSIONS.get(self.mime_type)

        if any([dim_tuple.width, dim_tuple.height, dim_tuple.allow_crop]):
            width = dim_tuple.width or ''
            height = dim_tuple.height or ''
            crop_flag = self.CROP_FLAG_ALLOW if dim_tuple.allow_crop else self.CROP_FLAG_DISALLOW
            dimensions = f'{width}{crop_flag}{height}{extension}'
        else:
            dimensions = f'full{extension}'

        return {
            'attachment_id': self.id,
            'dimensions': dimensions}

    def derivative_url(self, canned_dimensions, **kwargs):
        """
        Convenience function to build URLs that refer to this instance.

        It could be argued that this is an inappropriate coupling to the site
        blueprint and its routes, but placing this method here *dramatically*
        simplifies the template code that builds image links.

        Args:
            canned_dimensions: String containing one of the dimensions names
                from `CANNED_DIMENSIONS_MAP`.
            kwargs: Arbitrary keyword arguments that are passed directly into
                url_for().

        Returns:
            String URL that identified this Attachment and one specific
            Derivative related to it.
        """
        from flask import url_for

        kwargs.update(self.to_url_kwargs(canned_dimensions))

        return url_for('site.get_attachment_derivative', **kwargs)

    def derivative_info(self, canned_dimensions):
        """
        Convenience function to get the MIME type and file size of a Derivative.

        Another instance of potentially inappropritate coupling, this time to
        the AttachmentController. This function needs to generate a Derivative
        on the fly if one does not exist already, a responsibility we have given
        exclusively to the controller. As argued elsewhere, the simplicity
        gained in the template code is well worth the impurity here.

        Args:
            canned_dimensons: String containing one of the dimensions names
                from `CANNED_DIMENSIONS_MAP`.

        Returns:
            Tuple of (MIME type, file size in bytes).
        """
        from windowbox.controllers.attachment import AttachmentController

        derivative = AttachmentController.make_or_get_derivative(
            attachment=self,
            dim_tuple=self.CANNED_DIMENSIONS_MAP[canned_dimensions])

        return derivative.mime_type, derivative.storage_data_size_bytes

    def has_exif(self, category):
        """
        Does the given `category` contain at least one EXIF field?

        Args:
            category: String category name of interest.

        Returns:
            True if there is at least one field, False if there are none.
        """
        return len([*self.yield_exif(category)]) > 0

    def yield_exif(self, category):
        """
        Yield EXIF fields, one at a time, for the given `category`.

        Available categories, their content, and the ordering of returned fields
        are all governed by the content of `EXIF_CATEGORIES`.

        Args:
            category: String category name of interest.

        Yields:
            One EXIF_Field namedtuple per iteration, containing a result field
            from this instance's EXIF data.
        """
        category_data = EXIF_CATEGORIES.get(category)
        if category_data is None:
            logger.warning(
                f'Derivative ID {self.id} has no EXIF category data for {category}')
            return

        for field_candidates in category_data:
            for candidate in field_candidates:
                description = self.exif.get(f'{candidate}.desc')
                value = self.exif.get(f'{candidate}.val')
                raw_value = self.exif.get(f'{candidate}.num', value)

                if all([description, value]):
                    yield EXIF_Field(
                        attribute=candidate, description=description,
                        value=value, raw_value=raw_value)

                    # Once we've found one, no need for more field candidates
                    break
