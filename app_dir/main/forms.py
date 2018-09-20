from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError
from app_dir.models import User
from flask_login import current_user


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        if username.data != current_user.username and \
                User.query.filter_by(username=username.data).first() is not None:
            raise ValidationError('Username occupied, please use a different one.')


class PostForm(FlaskForm):
    post = TextAreaField('Say something',
                         validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')

