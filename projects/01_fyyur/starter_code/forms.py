from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL, ValidationError, Regexp
from enums import GenreEnum, StateEnum
import re

class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices = StateEnum.choices(),
        coerce = StateEnum.coerce
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone', validators=[DataRequired()] 
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices = GenreEnum.choices(),
        coerce = GenreEnum.coerce
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    website = StringField(
        'website', validators=[URL()]
    )
    image_link = StringField(
        'image_link', validators=[URL(), DataRequired()]
    )
    seeking_talent = BooleanField(
        'seeking_talent', default=False
    )
    seeking_description = StringField(
        'seeking_description'
    )

    def validate_phone(self, phone):
        us_phone_num = '^([0-9]{3})[-][0-9]{3}[-][0-9]{4}$'
        match = re.search(us_phone_num, phone.data)
        if not match:
            raise ValidationError('Error, phone number must be in format xxx-xxx-xxxx')

class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices = StateEnum.choices(),
        coerce = StateEnum.coerce
    )
    phone = StringField(
        'phone', validators=[DataRequired()] 
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices = GenreEnum.choices(),
        coerce = GenreEnum.coerce
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    website = StringField(
        'website', validators=[URL()]
    )
    image_link = StringField(
        'image_link', validators=[URL(), DataRequired()]
    )
    seeking_venue = BooleanField(
        'seeking_venue', default=False
    )
    seeking_description = StringField(
        'seeking_description'
    )

    def validate_phone(self, phone):
        us_phone_num = '^([0-9]{3})[-][0-9]{3}[-][0-9]{4}$'
        match = re.search(us_phone_num, phone.data)
        if not match:
            raise ValidationError('Error, phone number must be in format xxx-xxx-xxxx')
