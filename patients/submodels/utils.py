def medical_form_upload_path(instance, filename):
    return '/'.join(['medical_forms', str(instance.patient_username.patient_username), filename])

def prescribtion_form_upload_path(instance, filename):
    return '/'.join(['prescriptions', str(instance.consultation.patient_username), filename])

def lab_test_upload_path(instance, filename):
    return '/'.join(['lab_tests', str(instance.consultation.patient_username.patient_username), filename])

def upload_path(instance, filename):
    return '/'.join(['profile_pictures/dependents', str(instance.user.username), filename])



AI_CONSULTATION = 'ai'
IN_PERSON = 'inperson'
ONLINE = 'online'

CONSULTATION_TYPE = (
    # (AI_CONSULTATION, 'AI Consultation'),
    (IN_PERSON, 'In Person'),
    (ONLINE, 'Online'),
    )

CONSULTATION_STATUS = (
    ('pending', 'Pending'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
    ('rescheduled', 'Rescheduled'),
    ('inprogress', 'In Progress'),
    )

PAIN_AREA_CHOICES = (
    ('Abdomen', 'Abdomen'),
    ('Back', 'Back'),
    ('Chest', 'Chest'),
    ('Head', 'Head'),
    ('Joint', 'Joint'),
    ('Muscle', 'Muscle'),
    ('Neck', 'Neck'),
    ('Pelvis', 'Pelvis'),
    ('Shoulder', 'Shoulder'),
    ('Throat', 'Throat'),
    ('Respiratory', 'Respiratory'),
    ('Stomach', 'Stomach'),
    ('Unknown', 'Other'),
    )
