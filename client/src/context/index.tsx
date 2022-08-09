import { MaterialUIContextProvider } from './materialUI';
import React from 'react';

interface IProps {
  children: React.ReactNode;
}

export const ContextProvider: React.FC<IProps> = ({ children }) => {
  return <MaterialUIContextProvider>{children}</MaterialUIContextProvider>;
};
