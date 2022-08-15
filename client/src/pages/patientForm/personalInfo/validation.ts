import * as Yup from 'yup';

import { PatientField } from '../state';
import { getAgeBasedOnDOB } from 'src/shared/utils';

const ageIsValid = (age: number): boolean => {
  return age >= 0;
};

export const personalInfoValidationSchema = (creatingNew: boolean) =>
  Yup.object().shape({
    // no validation if patient ID field is disabled when editing existing patient
    [PatientField.patientId]: !creatingNew
      ? Yup.string()
      : Yup.number()
          .typeError('A valid patient ID is required.')
          .integer('A valid patient ID is required.')
          .test(
            'length',
            'A valid patient ID is required.',
            (pId) => String(pId).length > 0 && String(pId).length <= 15
          ),
    // For writing + testing Regex, see: regex101.com
    [PatientField.patientName]: Yup.string()
      .label('Name')
      .matches(/^\w[\w.'\- ]*$/, 'Name is not valid.')
      .required(),
    [PatientField.isExactDob]: Yup.boolean(),
    [PatientField.dob]: Yup.date().when(PatientField.isExactDob, {
      is: true,
      then: Yup.date().test(
        'valid-dob',
        'Please enter a valid date of birth.',
        (date) => !!date && ageIsValid(getAgeBasedOnDOB(date.toDateString()))
      ),
    }),
    [PatientField.estimatedAge]: Yup.number().when(PatientField.isExactDob, {
      is: false,
      then: Yup.number()
        .integer('Please enter a valid age.')
        .test(
          'valid-age',
          'Please enter a valid age.',
          (age) => !!age && ageIsValid(age)
        ),
    }),
    [PatientField.villageNumber]: Yup.number()
      .typeError('Village number must be numeric')
      .integer('Village number must be numeric')
      .min(1, 'Village number must be numeric'),
    [PatientField.isPregnant]: Yup.boolean(),
  });
