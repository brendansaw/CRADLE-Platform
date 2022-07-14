import React from 'react';
import { Typography } from '@material-ui/core';
import { CustomizedForm } from 'src/shared/types';
import { getPrettyDateTime } from 'src/shared/utils';
import { useHistory } from 'react-router-dom';
import AssignmentIcon from '@material-ui/icons/Assignment';
import { PrimaryButton } from '../../../shared/components/Button/index';

interface IProps {
  form: CustomizedForm;
}

export const CustomizedFormData = ({ form }: IProps) => {
  const history = useHistory();

  const handleEditFormClick = () => {
    if (form) {
      history.push(`/forms/edit/${form.patientId}/${form.id}`);
    }
  };

  return (
    <>
      <>
        <Typography variant="h5">
          <>
            <AssignmentIcon fontSize="large" /> {form.name}
          </>
        </Typography>
        <Typography variant="subtitle1">
          {`Last Edit : ${getPrettyDateTime(form.lastEdited)}`}
        </Typography>
        <Typography variant="subtitle1">
          {`Category : ${form.category}`}
        </Typography>

        <PrimaryButton onClick={handleEditFormClick}>
          View & Edit Form
        </PrimaryButton>
      </>
    </>
  );
};
