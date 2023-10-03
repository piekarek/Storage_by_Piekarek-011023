from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class PrimerForm(FlaskForm):
    application = StringField('Application', validators=[DataRequired()])
    pcr = StringField('PCR')
    target = StringField('Target')
    oligos = StringField('Oligos')
    sequence = TextAreaField('Sequence', validators=[DataRequired()])
    box = StringField('Box')
    position = StringField('Position')
    reference = StringField('Reference')
    comment = TextAreaField('Comment')
    submit = SubmitField('Add Primer')