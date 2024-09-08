from django.utils.translation import gettext_lazy as _


class Messages(object):
    DIANOSTIC_TEXT = _("Act as a doctor and give me just a possible diagnosis to tell what the patient sick of: \n")
    PRESCRIPTION_TEXT = _("Act as a doctor and give me just a possible prescription of medication to take, put all the prescription in a list of object e.g [{'prescription': the medication, 'frequence': number of time, 'type': either daily, monthly or yearly}]: \n")
    RECOMMENDATION_TEXT = _("Act as a doctor and give me just possible recommendation to follow: \n")
    RECOMMENDED_TESTS_TEXT = _("Act as a doctor and give me just a possible recommended tests: \n")
    PATIENT_DOES_NOT_EXIST = _("Patient does not exist")
    AI_ERROR_MESSAGE = _('Our doctor is having many requests at the moment.Please try again.')
    PAYMENT_FAILED = _('Payment failed. Make sure you have enough funds in your account and try again')
    DOCTOR_AI_NAME = _('Dr Emile')
    