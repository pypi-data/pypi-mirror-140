from cpg_pipes.hb.batch import setup_batch
from cpg_pipes.hb.command import wrap_command
from cpg_pipes.images import DRIVER_IMAGE

b = setup_batch('Copy nagim subset')

j = b.new_job('Copy nagim subset')
j.image(DRIVER_IMAGE)
j.command(wrap_command('''
gsutil -u nagim-331712 cp -r \
gs://cpg-nagim-main/mt/v1-1-amp-pd-mgrb.mt \
gs://cpg-nagim-release-requester-pays/mt/v1-1-amp-pd-mgrb.mt
''', setup_gcp=True))

b.run(wait=False)
