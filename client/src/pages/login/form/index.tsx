import * as Yup from 'yup';

import {
  LoginData,
  clearCurrentUserError,
  loginUser,
} from 'src/redux/reducers/user/currentUser';
import { useDispatch, useSelector } from 'react-redux';

import { OrNull } from 'src/shared/types';
import React from 'react';
import { ReduxState } from 'src/redux/reducers';
import { Toast } from 'src/shared/components/toast';
import classes from './styles.module.css';
import { useFormik } from 'formik';
import { PrimaryButton } from 'src/shared/components/Button';

export const LoginForm: React.FC = () => {
  const errorMessage = useSelector(
    ({ user }: ReduxState): OrNull<string> => user.current.message
  );
  const dispatch = useDispatch();
  const formik = useFormik({
    initialValues: {
      email: '',
      password: '',
    },
    validationSchema: Yup.object({
      email: Yup.string().required('Email is required.'),
      password: Yup.string().required('Password is required.'),
    }),
    onSubmit: (values: LoginData) => {
      dispatch(loginUser(values));
    },
  });

  const clearError = (): void => {
    dispatch(clearCurrentUserError());
  };

  return (
    <>
      <Toast
        severity="error"
        message={errorMessage ?? ''}
        open={Boolean(errorMessage)}
        onClose={clearError}
        transitionDuration={0}
      />
      <form onSubmit={formik.handleSubmit}>
        <h1 className={classes.login}>Log In</h1>
        <h2>Email</h2>
        <input
          className={classes.inputStyle}
          placeholder="somebody@example.com"
          {...formik.getFieldProps('email')}
        />
        {formik.touched.email && formik.errors.email ? (
          <div className={classes.formError}>{formik.errors.email}</div>
        ) : null}
        <h2>Password</h2>
        <input
          className={classes.inputStyle}
          placeholder="********"
          type="password"
          {...formik.getFieldProps('password')}
        />
        {formik.touched.password && formik.errors.password ? (
          <div className={classes.formError}>{formik.errors.password}</div>
        ) : null}
        <br />
        <PrimaryButton className="contant-submit white" type="submit">
          Login
        </PrimaryButton>
      </form>
    </>
  );
};
