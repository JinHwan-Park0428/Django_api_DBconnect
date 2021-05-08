# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from . import file_upload_path_for_db


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group_id = models.IntegerField()
    permission_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group_id', 'permission_id'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type_id = models.IntegerField()
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type_id', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user_id = models.IntegerField()
    group_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user_id', 'group_id'),)


class AuthUserUserPermissions(models.Model):
    user_id = models.IntegerField()
    permission_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user_id', 'permission_id'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type_id = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class SkdevsecBag(models.Model):
    bag_id = models.AutoField(primary_key=True)
    uid = models.CharField(max_length=50)
    pid = models.IntegerField()
    bcount = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'skdevsec_bag'


class SkdevsecBoard(models.Model):
    bid = models.AutoField(primary_key=True)
    btitle = models.CharField(max_length=100)
    btext = models.CharField(max_length=5000)
    bfile = models.FileField(upload_to=file_upload_path_for_db, blank=False, null=False)
    bview = models.IntegerField()
    bcomment = models.IntegerField()
    unickname = models.CharField(max_length=50)
    bcreate_date = models.CharField(max_length=50)
    bcate = models.CharField(max_length=50)
    b_lock = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'skdevsec_board'


class SkdevsecComment(models.Model):
    cid = models.AutoField(primary_key=True)
    bid = models.IntegerField()
    unickname = models.CharField(max_length=50)
    ctext = models.CharField(max_length=300)
    ccreate_date = models.CharField(max_length=50)
    clock = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'skdevsec_comment'


class SkdevsecOrderproduct(models.Model):
    opid = models.AutoField(primary_key=True)
    oid = models.IntegerField()
    pname = models.CharField(max_length=50)
    pcate = models.CharField(max_length=50)
    pprice = models.IntegerField()
    pcount = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'skdevsec_orderproduct'


class SkdevsecOrderuser(models.Model):
    oid = models.AutoField(primary_key=True)
    uid = models.CharField(max_length=50)
    oname = models.CharField(max_length=50)
    ophone = models.CharField(max_length=50)
    oaddress = models.CharField(max_length=50)
    order_date = models.CharField(max_length=50)
    oprice = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'skdevsec_orderuser'


class SkdevsecProduct(models.Model):
    pid = models.AutoField(primary_key=True)
    pname = models.CharField(max_length=50)
    pcate = models.CharField(max_length=50)
    pimage = models.FileField(upload_to=file_upload_path_for_db, blank=False, null=False)
    ptext = models.CharField(max_length=50)
    pprice = models.IntegerField()
    pcreate_date = models.CharField(max_length=50)
    preview = models.IntegerField()
    preview_avg = models.FloatField()
    pcount = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'skdevsec_product'


class SkdevsecReview(models.Model):
    rid = models.AutoField(primary_key=True)
    pid = models.IntegerField()
    rstar = models.FloatField()
    unickname = models.CharField(max_length=50)
    rcreate_date = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'skdevsec_review'


class SkdevsecUser(models.Model):
    uid = models.CharField(primary_key=True, max_length=50)
    upwd = models.CharField(max_length=50)
    unickname = models.CharField(max_length=50)
    uname = models.CharField(max_length=50)
    umail = models.CharField(max_length=50)
    uphone = models.CharField(max_length=50)
    ucreate_date = models.CharField(max_length=50)
    authority = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'skdevsec_user'
