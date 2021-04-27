from django.db import models

# fileupload = models.FileField(max_length=50, allow_empty_file=False, use_url=)


class SkdevsecBag(models.Model):
    bag_id = models.AutoField(primary_key=True)
    uid = models.IntegerField()
    pid = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'skdevsec_bag'


class SkdevsecBoard(models.Model):
    bid = models.AutoField(primary_key=True)
    btitle = models.CharField(max_length=100)
    btext = models.CharField(max_length=5000)
    bfile = models.CharField(max_length=100)
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
    pimage = models.CharField(max_length=50)
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
