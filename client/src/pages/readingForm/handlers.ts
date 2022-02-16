import { apiFetch, API_URL } from 'src/shared/api';
import { EndpointEnum } from 'src/shared/enums';
import { ReadingField, ReadingState } from './state';
import { getSymptomsFromFormState } from './symptoms/symptoms';

// not sure why the GUID is being generated client side... this should be moved server side
const guid = () => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
};

const getSubmitObject = (patientId: string, values: ReadingState) => {
  const currentTimestamp = Math.floor(Date.now() / 1000);
  const readingGuid = guid();

  // user ID and healthcare worker ID should be moved to the backend
  const submitValues = {
    reading: {
      patientId: patientId,
      readingId: readingGuid,
      dateTimeTaken: currentTimestamp,
      bpDiastolic: values[ReadingField.bpDiastolic],
      bpSystolic: values[ReadingField.bpSystolic],
      heartRateBPM: values[ReadingField.heartRateBPM],
      symptoms: getSymptomsFromFormState(values, true),
    },
    assessment: {
      dateAssessed: currentTimestamp,
      diagnosis: values[ReadingField.finalDiagnosis],
      followupInstructions: values[ReadingField.followUpInstruc],
      followupNeeded: values[ReadingField.followUp],
      medicationPrescribed: values[ReadingField.drugHistory],
      specialInvestigations: values[ReadingField.investigation],
      treatment: values[ReadingField.treatment],
      patientId: patientId,
    },
  } as any;

  if (values[ReadingField.urineTest]) {
    submitValues['reading']['urineTests'] = {
      urineTestBlood: values[ReadingField.blood],
      urineTestGlu: values[ReadingField.glucose],
      urineTestLeuc: values[ReadingField.leukocytes],
      urineTestNit: values[ReadingField.nitrites],
      urineTestPro: values[ReadingField.protein],
    };
  }

  return submitValues;
};

export const handleSubmit = async (
  patientId: string,
  values: ReadingState,
  drugHistory: string
) => {
  const submitValues = getSubmitObject(patientId, values);
  const url = API_URL + EndpointEnum.READING_ASSESSMENT;

  try {
    await apiFetch(url, {
      method: 'POST',
      body: JSON.stringify(submitValues),
    });

    const newDrugHistory = values[ReadingField.drugHistory];
    if (drugHistory !== newDrugHistory) {
      await apiFetch(
        API_URL +
          EndpointEnum.PATIENTS +
          `/${patientId}` +
          EndpointEnum.MEDICAL_RECORDS,
        {
          method: 'POST',
          body: JSON.stringify({
            [ReadingField.drugHistory]: newDrugHistory,
          }),
        }
      );
    }
  } catch (e) {
    console.error(e);
    return false;
  }

  return true;
};
