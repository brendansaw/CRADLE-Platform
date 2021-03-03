import React, { useEffect, useState } from 'react';
import { apiFetch } from 'src/shared/utils/api';
import { BASE_URL } from 'src/server/utils';
import { EndpointEnum } from 'src/server';
import MUIDataTable from 'mui-datatables';
import { makeStyles } from '@material-ui/core/styles';
import { Button, IconButton, Tooltip } from '@material-ui/core';
import AddIcon from '@material-ui/icons/Add';
import CreateIcon from '@material-ui/icons/Create';
import { Toast } from 'src/shared/components/toast';

interface IFacility {
  about: string;
  facilityType: string;
  healthFacilityName: string;
  healthFacilityPhoneNumber: string;
  location: string;
}

const columns = [
  'Facility Name',
  'Phone Number',
  'Location',
  {
    name: 'Take Action',
    options: {
      sort: false,
    },
  },
];

export const ManageFacilities = () => {
  const styles = useStyles();
  const [errorLoading, setErrorLoading] = useState(false);
  const [facilities, setFacilities] = useState<IFacility[]>([]);
  const [data, setData] = useState<(string | number)[][]>([]);

  useEffect(() => {
    const getFacilities = async () => {
      try {
        const resp: IFacility[] = await (
          await apiFetch(BASE_URL + EndpointEnum.HEALTH_FACILITIES)
        ).json();
        setFacilities(resp);
      } catch (e) {
        setErrorLoading(true);
      }
    };

    getFacilities();
  }, []);

  useEffect(() => {
    const rows = facilities.map((f, idx) => [
      f.healthFacilityName,
      f.healthFacilityPhoneNumber,
      f.location,
      idx,
    ]);
    setData(rows);
  }, [facilities]);

  const CreateFacilityButton = () => (
    <Button
      className={styles.button}
      color="primary"
      variant="contained"
      size="large"
      onClick={() => alert('create')}>
      <AddIcon />
      New Facility
    </Button>
  );

  const Row = ({ row }: { row: (string | number)[] }) => {
    const cells = row.slice(0, -1);
    const facility = facilities[row.slice(-1)[0] as number];

    return (
      <tr className={styles.row}>
        {cells.map((item, i) => (
          <td className={styles.cell} key={i}>
            {item}
          </td>
        ))}
        <td className={styles.cell}>
          <Tooltip placement="top" title="Edit Facility">
            <IconButton onClick={() => alert(facility.healthFacilityName)}>
              <CreateIcon />
            </IconButton>
          </Tooltip>
        </td>
      </tr>
    );
  };

  return (
    <div className={styles.tableContainer}>
      {errorLoading && (
        <Toast
          status="error"
          message="Something went wrong loading the health care facilities. Please try again."
          clearMessage={() => setErrorLoading(false)}
        />
      )}
      <MUIDataTable
        title="Health Care Facilities"
        columns={columns}
        data={data}
        options={{
          search: false,
          download: false,
          print: false,
          viewColumns: false,
          filter: false,
          selectToolbarPlacement: 'none',
          selectableRows: 'none',
          rowHover: false,
          responsive: 'standard',
          customToolbar: () => <CreateFacilityButton />,
          customRowRender: (row, i) => <Row key={i} row={row} />,
        }}
      />
    </div>
  );
};

const useStyles = makeStyles({
  tableContainer: {
    '& .MuiTableCell-head': {
      fontWeight: 'bold',
    },
    '& .MuiTableSortLabel-icon': {
      marginTop: 15,
    },
  },
  row: {
    borderBottom: '1px solid #ddd',
  },
  cell: {
    padding: '4px 16px',
  },
  button: {
    height: '100%',
  },
});
