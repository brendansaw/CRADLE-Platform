import {
  Divider,
  Form,
  Header,
  Input,
  InputOnChangeData,
  Select,
  TextArea,
} from 'semantic-ui-react';
import { GestationalAgeUnitEnum, SexEnum } from '../../../../enums';
import {
  gestationalAgeUnitOptions,
  pregnantOptions,
  sexOptions,
} from './utils';
import {
  gestationalAgeValueMonthOptions,
  gestationalAgeValueWeekOptions,
  getNumOfMonths,
  getNumOfWeeks,
} from '../../../utils';

import { EditedPatient } from '@types';
import Paper from '@material-ui/core/Paper';
import React from 'react';
import { useStyles } from './styles';

export const GESTATIONAL_AGE_UNITS = {
  WEEKS: 'GESTATIONAL_AGE_UNITS_WEEKS',
  MONTHS: 'GESTATIONAL_AGE_UNITS_MONTHS',
};

interface IProps {
  patient: EditedPatient;
  onChange: (
    event: React.ChangeEvent<HTMLInputElement>,
    { name, value }: InputOnChangeData
  ) => void;
  isEditPage?: boolean;
}

export const PatientInfoForm: React.FC<IProps> = ({
  patient,
  onChange,
  isEditPage,
}) => {
  const classes = useStyles();

  const dob = React.useMemo((): string => {
    if (patient.dob) {
      return `${patient.dob}`;
    }

    return ``;
  }, [patient]);

  const patientAge = React.useMemo((): string => {
    return patient.patientAge ? patient.patientAge.toString() : ``;
  }, [patient]);

  const gestationalTimestamp = React.useMemo((): string => {
    return patient.gestationalAgeUnit === GestationalAgeUnitEnum.WEEKS
      ? getNumOfWeeks(patient.gestationalTimestamp).toString()
      : getNumOfMonths(patient.gestationalTimestamp).toString();
  }, [patient.gestationalAgeUnit, patient.gestationalTimestamp]);

  return (
    <Paper className={classes.container}>
      {!isEditPage && (
        <Header>
          <b>Patient Information</b>
        </Header>
      )}
      {!isEditPage && <Divider />}
      <Form.Group>
        <Form.Field
          className={classes.input}
          name="patientName"
          value={patient.patientName}
          control={Input}
          label="Patient Initials"
          placeholder="Patient Initials"
          onChange={onChange}
          type="text"
          pattern="[a-zA-Z]*"
          maxLength="4"
          minLength="1"
          required={true}
        />
        {!isEditPage && (
          <Form.Field
            className={classes.input}
            name="patientId"
            value={patient.patientId}
            control={Input}
            label="ID"
            placeholder="ID Number"
            onChange={onChange}
            type="text"
            maxLength="15"
            minLength="1"
            required={true}
          />
        )}
      </Form.Group>
      <Form.Group widths="equal">
        <Form.Field
          className={classes.input}
          name="patientAge"
          value={patientAge}
          control={Input}
          label="Age"
          type="number"
          min="15"
          max="60"
          placeholder="Patient Age"
          onChange={onChange}
        />
        <Form.Field
          className={classes.input}
          name="dob"
          value={dob}
          control={Input}
          label="Birthday"
          type="date"
          placeholder="Birthday"
          onChange={onChange}
        />
        <Form.Field
          className={classes.input}
          name="patientSex"
          value={patient.patientSex}
          control={Select}
          label="Gender"
          options={sexOptions}
          placeholder="Gender"
          onChange={onChange}
          required={true}
        />
      </Form.Group>
      <Form.Group widths="equal">
        <Form.Field
          className={classes.input}
          name="isPregnant"
          value={patient.isPregnant}
          control={Select}
          label="Pregnant"
          options={pregnantOptions}
          onChange={onChange}
          disabled={patient.patientSex === SexEnum.MALE}
          required={patient.patientSex === SexEnum.FEMALE}
        />
        <Form.Dropdown
          name="gestationalTimestamp"
          value={gestationalTimestamp}
          control={Select}
          options={
            patient.gestationalAgeUnit === GestationalAgeUnitEnum.WEEKS
              ? gestationalAgeValueWeekOptions
              : gestationalAgeValueMonthOptions
          }
          search={true}
          onChange={onChange}
          label="Gestational Age"
          disabled={patient.patientSex === SexEnum.MALE || !patient.isPregnant}
          required={patient.patientSex === SexEnum.FEMALE && patient.isPregnant}
        />
        <Form.Field
          className={classes.input}
          name="gestationalAgeUnit"
          value={patient.gestationalAgeUnit}
          control={Select}
          options={gestationalAgeUnitOptions}
          onChange={onChange}
          label="Gestational Age Unit"
          disabled={patient.patientSex === SexEnum.MALE || !patient.isPregnant}
          required={patient.patientSex === SexEnum.FEMALE && patient.isPregnant}
        />
      </Form.Group>
      <Form.Group>
        <Form.Field
          className={classes.input}
          name="zone"
          value={patient.zone}
          control={Input}
          label="Zone"
          type="number"
          placeholder="Zone"
          onChange={onChange}
        />
        <Form.Field
          className={classes.input}
          name="villageNumber"
          value={patient.villageNumber}
          control={Input}
          label="Village"
          type="number"
          placeholder="Village"
          onChange={onChange}
        />
      </Form.Group>
      <Form.Field
        className={classes.input}
        name="drugHistory"
        value={patient.drugHistory}
        control={TextArea}
        label="Drug History"
        placeholder="Enter the patient's drug history..."
        onChange={onChange}
      />
      <Form.Field
        className={classes.input}
        name="medicalHistory"
        value={patient.medicalHistory}
        control={TextArea}
        label="Medical History"
        placeholder="Enter the patient's medical history..."
        onChange={onChange}
      />
    </Paper>
  );
};
