"""
Tests for the Attachment model.
"""

from unittest.mock import Mock, patch
from windowbox.models.attachment import Attachment, EXIF_Field


def test_attachment_storage(db, post_instance):
    """
    Should be able to save an Attachment then re-read it verbatim.
    """
    assume_id = 1
    post = post_instance
    mime_type = 'image/jpeg'
    orientation = 1
    geo_latitude = 36
    geo_longitude = -78.9
    geo_address = 'Land of pytest'
    exif = {
        'attr1': 'val1',
        'attr2': 'val2',
        'attr3': 'val3'}

    in_attachment = Attachment(
        post=post,
        mime_type=mime_type,
        orientation=orientation,
        geo_latitude=geo_latitude,
        geo_longitude=geo_longitude,
        geo_address=geo_address,
        exif=exif)
    db.session.add(in_attachment)
    db.session.flush()

    out_attachment = Attachment.query.filter_by(id=assume_id).one()

    assert out_attachment.id == assume_id
    assert out_attachment.post == post
    assert out_attachment.mime_type == mime_type
    assert out_attachment.orientation == orientation
    assert float(out_attachment.geo_latitude) == geo_latitude
    assert float(out_attachment.geo_longitude) == geo_longitude
    assert out_attachment.geo_address == geo_address
    assert out_attachment.exif == exif


def test_attachment_new_derivative(attachment_instance):
    """
    Should be able to make a new Derivative bound to this Attachment.
    """
    derivative = attachment_instance.new_derivative(width=987, height=654)

    assert derivative.attachment == attachment_instance
    assert derivative.mime_type == attachment_instance.mime_type
    assert derivative.width == 987
    assert derivative.height == 654


def test_attachment_populate_exif(db, tmp_path, attachment_instance):
    """
    Should be able to load the EXIF data and extract the orientation.
    """

    # Set up the Attachment fixture so it has a working storage path
    attachment_instance.base_path = tmp_path
    db.session.add(attachment_instance)
    db.session.flush()

    mock_exif = {
        'Composite:GPSLatitude.num': 36,
        'Composite:GPSLongitude.num': -78.9}

    mock_client = Mock()
    mock_client.read_file.return_value = mock_exif
    attachment_instance.populate_exif(exiftool_client=mock_client)

    # Assertions for EXIF with no orientation field
    assert attachment_instance.exif == mock_exif
    assert attachment_instance.orientation is None

    mock_exif['EXIF:Orientation.num'] = 2

    attachment_instance.populate_exif(exiftool_client=mock_client)

    # Assertions for EXIF with orientation
    assert attachment_instance.exif == mock_exif
    assert attachment_instance.orientation == 2


def test_attachment_populate_geo(attachment_instance):
    """
    Should be able to load the geographic data from EXIF lat/long.
    """
    mock_client = Mock()
    mock_client.latlng_to_address.return_value = 'pytestburg'

    attachment_instance.exif = {}
    attachment_instance.populate_geo(gmapi_client=mock_client)

    # Assertions for EXIF with no lat/long
    mock_client.latlng_to_address.assert_not_called()
    assert attachment_instance.geo_latitude is None
    assert attachment_instance.geo_longitude is None
    assert attachment_instance.geo_address is None

    attachment_instance.exif = {
        'Composite:GPSLatitude.num': 36,
        'Composite:GPSLongitude.num': -78.9}
    attachment_instance.populate_geo(gmapi_client=mock_client)

    # Assertions for EXIF with lat/long
    mock_client.latlng_to_address.assert_called_with(latitude=36, longitude=-78.9)
    assert float(attachment_instance.geo_latitude) == 36
    assert float(attachment_instance.geo_longitude) == -78.9
    assert attachment_instance.geo_address == 'pytestburg'


def test_attachment_to_url_kwargs(attachment_instance):
    """
    Should be able to encode itself into kwargs for url_for().
    """
    attachment_instance.id = 3456

    assert attachment_instance.to_url_kwargs('full') == {
        'attachment_id': 3456, 'dimensions': 'full.jpg'}
    assert attachment_instance.to_url_kwargs('opengraph') == {
        'attachment_id': 3456, 'dimensions': '750~750.jpg'}
    assert attachment_instance.to_url_kwargs('single') == {
        'attachment_id': 3456, 'dimensions': '960~720.jpg'}
    assert attachment_instance.to_url_kwargs('single2x') == {
        'attachment_id': 3456, 'dimensions': '1920~1440.jpg'}
    assert attachment_instance.to_url_kwargs('thumbnail') == {
        'attachment_id': 3456, 'dimensions': '300x300.jpg'}
    assert attachment_instance.to_url_kwargs('thumbnail2x') == {
        'attachment_id': 3456, 'dimensions': '600x600.jpg'}


def test_attachment_derivative_url(attachment_instance):
    """
    Should be able to build a URL to itself.
    """
    attachment_instance.to_url_kwargs = Mock(return_value={
        'attachment_id': 4567, 'dimensions': 'TESTxTEST.jpg'})

    with patch('flask.url_for') as mock_url_for:
        mock_url_for.return_value = '/test/url/here'
        assert attachment_instance.derivative_url('testsize1', _external=True) == '/test/url/here'
        mock_url_for.assert_called_with(
            'site.get_attachment_derivative', attachment_id=4567,
            dimensions='TESTxTEST.jpg', _external=True)


def test_attachment_derivative_info(attachment_instance):
    """
    Should be able to produce MIME type and file size for storage data.
    """
    derivative = Mock()
    derivative.mime_type = 'image/png'
    derivative.storage_data_size_bytes = 654321

    with patch(
            'windowbox.controllers.attachment.AttachmentController.make_or_get_derivative',
            return_value=derivative) as mock_mogd:
        out_mime, out_size = attachment_instance.derivative_info('thumbnail')
        mock_mogd.assert_called_with(
            attachment=attachment_instance,
            dim_tuple=Attachment.CANNED_DIMENSIONS_MAP['thumbnail'])

    assert out_mime == 'image/png'
    assert out_size == 654321


def test_attachment_has_exif(attachment_instance):
    """
    Should be able to indicate if there is anything for an EXIF category.
    """
    attachment_instance.exif = {
        'EXIF:FocalLength.desc': 'Focal Length',
        'EXIF:FocalLength.num': '4.2 mm',
        'EXIF:FocalLength.val': '4.2 mm'}

    assert attachment_instance.has_exif('camera')
    assert not attachment_instance.has_exif('image')


def test_attachment_yield_exif(attachment_instance):
    """
    Should be able to yield EXIF fields as warranted.
    """
    assert [*attachment_instance.yield_exif('abject crap')] == []

    attachment_instance.exif = {}
    assert [*attachment_instance.yield_exif('camera')] == []

    attachment_instance.exif = {
        # First choice in list of 1
        'EXIF:FocalLength.desc': 'Focal Length',
        'EXIF:FocalLength.num': '4.2 mm',
        'EXIF:FocalLength.val': '4.2 mm',

        # Second choice in list of 2
        'EXIF:ShutterSpeedValue.desc': 'Shutter Speed',
        'EXIF:ShutterSpeedValue.num': '1/30',
        'EXIF:ShutterSpeedValue.val': '1/30'}
    assert [*attachment_instance.yield_exif('camera')] == [
        EXIF_Field('EXIF:FocalLength', 'Focal Length', '4.2 mm', '4.2 mm'),
        EXIF_Field('EXIF:ShutterSpeedValue', 'Shutter Speed', '1/30', '1/30')]

    attachment_instance.exif = {
        # Second choice in list of 3
        'EXIF:ExifImageHeight.desc': 'Exif Image Height',
        'EXIF:ExifImageHeight.num': '3024',
        'EXIF:ExifImageHeight.val': '3024',

        # Non-whitelisted entry
        'EXIF:NoodlePoodle.desc': 'Noodle Poodle',
        'EXIF:NoodlePoodle.num': 'verily',
        'EXIF:NoodlePoodle.val': 'verily'}
    assert [*attachment_instance.yield_exif('image')] == [
        EXIF_Field('EXIF:ExifImageHeight', 'Exif Image Height', '3024', '3024')]
