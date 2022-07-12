import { API_URL, apiFetch } from 'src/shared/api';
import { CancelButton, PrimaryButton } from 'src/shared/components/Button';
import {
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@material-ui/core';
import { Field, Form, Formik } from 'formik';
import {
  IPasswordForm,
  PasswordField,
  initialValues,
  validationSchema,
} from './state';
import React, { useState } from 'react';

import Alert from '@material-ui/lab/Alert';
import { EndpointEnum } from 'src/shared/enums';
import { TextField } from 'formik-material-ui';
import { Toast } from 'src/shared/components/toast';

interface IProps {
  open: boolean;
  onClose: () => void;
}

const ChangePassword = ({ open, onClose }: IProps) => {
  const [submitError, setSubmitError] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const handleSubmit = async (values: IPasswordForm) => {
    const init = {
      method: 'POST',
      body: JSON.stringify({
        [PasswordField.currentPass]: values[PasswordField.currentPass],
        [PasswordField.newPass]: values[PasswordField.newPass],
      }),
    };

    try {
      await apiFetch(API_URL + EndpointEnum.CHANGE_PASS, init);

      setSubmitError(false);
      setSubmitSuccess(true);
      onClose();
    } catch (e) {
      setSubmitError(true);
    }
  };

  return (
    <>
      <Toast
        severity="success"
        message="Password change successful!"
        open={submitSuccess}
        onClose={() => setSubmitSuccess(false)}
      />
      <Dialog open={open} maxWidth="xs" fullWidth>
        <DialogTitle>Change Password</DialogTitle>
        <DialogContent>
          {submitError && (
            <>
              <Alert severity="error" onClose={() => setSubmitError(false)}>
                Unable to change your password. Did you enter your current
                password correctly?
              </Alert>
              <br />
              <br />
            </>
          )}
          <Formik
            initialValues={initialValues}
            validationSchema={validationSchema}
            onSubmit={handleSubmit}>
            {({ isSubmitting }) => (
              <Form
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  rowGap: '10px',
                }}>
                <Field
                  component={TextField}
                  type="password"
                  fullWidth
                  required
                  variant="outlined"
                  label="Current Password"
                  name={PasswordField.currentPass}
                />
                <Field
                  component={TextField}
                  type="password"
                  fullWidth
                  required
                  variant="outlined"
                  label="New Password"
                  name={PasswordField.newPass}
                />
                <Field
                  component={TextField}
                  type="password"
                  fullWidth
                  required
                  variant="outlined"
                  label="Confirm New Password"
                  name={PasswordField.confirmNewPass}
                />
                <DialogActions>
                  <CancelButton type="button" onClick={onClose}>
                    Cancel
                  </CancelButton>
                  <PrimaryButton type="submit" disabled={isSubmitting}>
                    Change
                  </PrimaryButton>
                </DialogActions>
              </Form>
            )}
          </Formik>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default ChangePassword;
