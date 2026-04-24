from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange


# ============================================
# FORMULARIO: LOGIN
# ============================================
class LoginForm(FlaskForm):
    email       = StringField('Email', validators=[DataRequired(), Email()])
    contrasena  = PasswordField('Contraseña', validators=[DataRequired()])
    recordarme  = BooleanField('Recordarme')


# ============================================
# FORMULARIO: REGISTRO
# ============================================
class RegistroForm(FlaskForm):
    nombre      = StringField('Nombre completo', validators=[DataRequired(), Length(min=3, max=100)])
    email       = StringField('Email', validators=[DataRequired(), Email()])
    telefono    = StringField('Teléfono', validators=[Optional(), Length(max=15)])
    contrasena  = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    confirmar   = PasswordField('Confirmar contraseña', validators=[DataRequired(), EqualTo('contrasena', message='Las contraseñas no coinciden')])


# ============================================
# FORMULARIO: RECUPERAR CONTRASEÑA
# ============================================
class RecuperarForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])


# ============================================
# FORMULARIO: NUEVA CONTRASEÑA
# ============================================
class NuevaContrasenaForm(FlaskForm):
    contrasena  = PasswordField('Nueva contraseña', validators=[DataRequired(), Length(min=6)])
    confirmar   = PasswordField('Confirmar contraseña', validators=[DataRequired(), EqualTo('contrasena', message='Las contraseñas no coinciden')])


# ============================================
# FORMULARIO: DIRECCIÓN
# ============================================
class DireccionForm(FlaskForm):
    nombre_completo         = StringField('Nombre completo', validators=[DataRequired(), Length(max=150)])
    direccion               = TextAreaField('Dirección', validators=[DataRequired()])
    numero_exterior         = StringField('Número exterior', validators=[Optional(), Length(max=20)])
    numero_interior         = StringField('Número interior', validators=[Optional(), Length(max=20)])
    ciudad                  = StringField('Ciudad', validators=[DataRequired(), Length(max=50)])
    provincia               = StringField('Provincia', validators=[Optional(), Length(max=50)])
    codigo_postal           = StringField('Código postal', validators=[DataRequired(), Length(max=10)])
    telefono                = StringField('Teléfono', validators=[DataRequired(), Length(max=15)])
    instrucciones_entrega   = TextAreaField('Instrucciones de entrega', validators=[Optional()])
    por_defecto             = BooleanField('Establecer como dirección por defecto')


# ============================================
# FORMULARIO: RESEÑA
# ============================================
class ResenaForm(FlaskForm):
    calificacion    = SelectField('Calificación', choices=[(1,'1'),(2,'2'),(3,'3'),(4,'4'),(5,'5')], coerce=int, validators=[DataRequired()])
    titulo          = StringField('Título', validators=[Optional(), Length(max=150)])
    contenido       = TextAreaField('Comentario', validators=[Optional()])


# ============================================
# FORMULARIO: CUPÓN
# ============================================
class CuponForm(FlaskForm):
    codigo = StringField('Código de cupón', validators=[DataRequired(), Length(max=50)])


# ============================================
# FORMULARIO: CONTACTO
# ============================================
class ContactoForm(FlaskForm):
    nombre      = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    email       = StringField('Email', validators=[DataRequired(), Email()])
    asunto      = StringField('Asunto', validators=[DataRequired(), Length(max=150)])
    mensaje     = TextAreaField('Mensaje', validators=[DataRequired()])