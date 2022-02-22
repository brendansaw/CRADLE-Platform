import { TrafficLightEnum } from 'src/shared/enums';

export interface IPatient {
  patientId: string;
  patientName: string;
  villageNumber: string;
  trafficLightStatus: TrafficLightEnum;
  dateTimeTaken: number | null;
}
