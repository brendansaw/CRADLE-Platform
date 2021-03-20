import * as Yup from 'yup';

export interface IUserGet {
  id: number;
  email: string;
  firstName: string;
  healthFacilityName: string;
  roleIds: number[];
  vhtList: number[];
}

export interface IUserRegister {
  email: string;
  password: string;
  firstName: string;
  healthFacilityName: string;
  role: string;
}

export interface IUserEdit {
  email: string;
  firstName: string;
  healthFacilityName: string;
  newRoleIds: number[];
  newVhtIds: number[];
}

export interface IVHT {
  id: number;
  email: string;
}

export enum UserField {
  firstName = 'firstName',
  email = 'email',
  healthFacilityName = 'healthFacilityName',
  role = 'role',
  supervises = 'supervises',
  password = 'password',
  confirmPassword = 'confirmPassword',
}

export enum UserRole {
  VHT = 'VHT',
  CHO = 'CHO',
  HCW = 'HCW',
  ADMIN = 'ADMIN',
}

export const userRoles = {
  [UserRole.VHT]: 'VHT',
  [UserRole.CHO]: 'CHO',
  [UserRole.HCW]: 'HCW',
  [UserRole.ADMIN]: 'Admin',
};

export const fieldLabels = {
  [UserField.firstName]: 'First Name',
  [UserField.email]: 'Email',
  [UserField.healthFacilityName]: 'Health Facility',
  [UserField.role]: 'Role',
  [UserField.supervises]: 'VHTs Supervised',
  [UserField.password]: 'Password',
  [UserField.confirmPassword]: 'Confirm Password',
};

const detailsValidationShape = (emailsInUse: string[]) => ({
  [UserField.firstName]: Yup.string()
    .label(fieldLabels[UserField.firstName])
    .required(),
  [UserField.email]: Yup.string()
    .label(fieldLabels[UserField.email])
    .required()
    .email('Please enter a valid email address')
    .notOneOf(emailsInUse, 'This email address is already in use'),
  [UserField.healthFacilityName]: Yup.string()
    .label(fieldLabels[UserField.healthFacilityName])
    .required(),
  [UserField.role]: Yup.string().label(fieldLabels[UserField.role]).required(),
});

const passwordValidationShape = {
  [UserField.password]: Yup.string()
    .label(fieldLabels[UserField.password])
    .required()
    .min(8),
  [UserField.confirmPassword]: Yup.string()
    .label(fieldLabels[UserField.confirmPassword])
    .required()
    .oneOf([Yup.ref(UserField.password)], 'Passwords must match'),
};

export const newEditValidationSchema = (
  creatingNew: boolean,
  emailsInUse: string[]
) => {
  let shape = detailsValidationShape(emailsInUse);

  if (creatingNew) {
    shape = {
      ...shape,
      ...passwordValidationShape,
    };
  }

  return Yup.object().shape(shape);
};

export const passwordValidationSchema = Yup.object().shape(
  passwordValidationShape
);
