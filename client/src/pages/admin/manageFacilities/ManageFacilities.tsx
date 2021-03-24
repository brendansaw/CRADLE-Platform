import React, { useEffect, useState } from 'react';
import { apiFetch } from 'src/shared/utils/api';
import { BASE_URL } from 'src/server/utils';
import { EndpointEnum } from 'src/server';
import { IconButton, Tooltip } from '@material-ui/core';
import CreateIcon from '@material-ui/icons/Create';
import { Toast } from 'src/shared/components/toast';
import { IFacility } from './state';
import EditFacility from './EditFacility';
import { getHealthFacilityList } from 'src/redux/reducers/healthFacilities';
import { useDispatch } from 'react-redux';
import { useAdminStyles } from '../adminStyles';
import AdminTable from '../AdminTable';

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
  const styles = useAdminStyles();
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(true);
  const [errorLoading, setErrorLoading] = useState(false);
  const [facilities, setFacilities] = useState<IFacility[]>([]);
  const [search, setSearch] = useState('');
  const [tableData, setTableData] = useState<(string | number)[][]>([]);
  const [editPopupOpen, setEditPopupOpen] = useState(false);
  const [facilityToEdit, setFacilityToEdit] = useState<IFacility>();

  const getFacilities = async () => {
    try {
      const resp: IFacility[] = await (
        await apiFetch(BASE_URL + EndpointEnum.HEALTH_FACILITIES)
      ).json();

      setFacilities(resp);
      setLoading(false);
    } catch (e) {
      setErrorLoading(true);
    }
  };

  useEffect(() => {
    getFacilities();
  }, []);

  useEffect(() => {
    const searchLowerCase = search.toLowerCase().trim();

    const facilityFilter = (facility: IFacility) => {
      return (
        facility.healthFacilityName.toLowerCase().startsWith(searchLowerCase) ||
        facility.location.toLowerCase().startsWith(searchLowerCase)
      );
    };

    const rows = facilities
      .filter(facilityFilter)
      .map((f, idx) => [
        f.healthFacilityName,
        f.healthFacilityPhoneNumber,
        f.location,
        idx,
      ]);
    setTableData(rows);
  }, [facilities, search]);

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
            <IconButton
              onClick={() => {
                setFacilityToEdit(facility);
                setEditPopupOpen(true);
              }}>
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
      <EditFacility
        open={editPopupOpen}
        onClose={() => {
          setEditPopupOpen(false);
          dispatch(getHealthFacilityList());
          getFacilities();
        }}
        facilities={facilities}
        editFacility={facilityToEdit}
      />
      <AdminTable
        title="Health Care Facilities"
        newBtnLabel="New Facility"
        newBtnOnClick={() => {
          setFacilityToEdit(undefined);
          setEditPopupOpen(true);
        }}
        search={search}
        setSearch={setSearch}
        columns={columns}
        Row={Row}
        data={tableData}
        loading={loading}
      />
    </div>
  );
};
