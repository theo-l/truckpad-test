# truckpad-test
Tech Test for truckpad interview

#API Docs

### 1. Truck arriving registration
- Endpoint: **POST** /api/register-entrance/
- Request Data Specification:
```json
{
  "truck_number": "DSZ3381", // truck's card numebr
  "truck_type": 1, // Truck's type number
  "cpf_no": "23725897840", // driver's cpf number for unique idenfication
  "name": "Liang", // driver's name
  "age": 30, // driver's age
  "gender": 1, // driver's gender: 0-secret, 1-male, 2-female
  "drive_license_type": "A/B", // driver's drive license type
  "has_truck": true, // if driver has truck or no
  "is_loaded": false, // if truck is loaded
  "user_from_terminal": "35ff14e0-664d-43c6-abad-e68ac8b61809", // driver's source terminal id
  "user_to_terminal": "4c91204e-f63b-4359-bdb9-76c166a2603d",// driver's destination terminal id
  "to_terminal": "35ff14e0-664d-43c6-abad-e68ac8b61809", // current exit terminal's id 
  "from_terminal": "4c91204e-f63b-4359-bdb9-76c166a2603d" // current arrived terminal's id 
}
``` 
- Response Data Sepcification:
```json
{
  "object_id": "080dc891-bcb4-44b1-8ef6-b194899eacbb", // registration id
  "created_at": 1545008709, // registration time's timestamp value
  "updated_at": 1545008709, // comm update time's timestamp value
  
  "driver": { 
    "object_id": "59f3e8bf-74f6-4b95-b1c9-6f0e6b86ce53",
    "created_at": 1545005672,
    "updated_at": 1545008709,
    "cpf_no": "23725897840",
    "name": "Liang",
    "age": 30,
    "gender": 1,
    "drive_license_type": "A/B",
    "has_truck": true,
    "from_terminal": "35ff14e0-664d-43c6-abad-e68ac8b61809",
    "to_terminal": "4c91204e-f63b-4359-bdb9-76c166a2603d"
  },
  "truck": {
    "object_id": "d3068505-a413-4de6-bf93-949f8da2b3ac",
    "created_at": 1545005101,
    "updated_at": 1545005101,
    "number": "DSZ3381",
    "truck_type": 1
  },
  "from_terminal": "4c91204e-f63b-4359-bdb9-76c166a2603d",
  "to_terminal": "35ff14e0-664d-43c6-abad-e68ac8b61809",
  "is_loaded": false,
  "status": 0
}
```

### 2. Query each driver's source and destination
- Endpoint: **GET** /api/query-driver-location/
- Request Data specification:
```json
{
  "cpf_no": "23725898830"
}
```
- Response data specification:
```json
{
  "status": 0,
  "cpf_no": "23725897840",
  "name": "Liang",
  "origin_terminal": {
    "name": "Taubaté",
    "latitude": 13.456,
    "longitude": 13.567
  },
  "destination_terminal": {
    "name": "Tietê",
    "latitude": 12.345,
    "longitude": 12.456
  }
}
```

### 3. Query Empty Return drivers
- Endpoint: **GET** /api/query-empty-return-drivers/
- Request data specification: **None**
- Response data specification:
```json
{
  "status": 0,
  "data": [
    {
      "object_id": "59f3e8bf-74f6-4b95-b1c9-6f0e6b86ce53",
      "created_at": 1545005672,
      "updated_at": 1545008709,
      "cpf_no": "23725897840",
      "name": "Liang",
      "age": 30,
      "gender": 1,
      "drive_license_type": "A/B",
      "has_truck": true,
      "from_terminal": "35ff14e0-664d-43c6-abad-e68ac8b61809",
      "to_terminal": "4c91204e-f63b-4359-bdb9-76c166a2603d"
    }
  ]
}
```

### 4. Query self-own truck drivers count
- Endpoint: **GET** /api/query-own-truck-drivers/
- Request data specification: **None**
- Response data specification:
```json
{
  "status": 0,
  "driver_count": 1
}
```


### 5. Query Loaded Trucks during one day, one week or one month
- Endpoint: **GET** /api/query-terminal-loaded-traffic/
- Request data specification:
```json
{
  "start_date": "2018-12-01", // **optional**, query period date, default is today
  "end_date": "2018-12-05", // **optional**, query period end, default is tomorrow
  "terminal": "4c91204e-f63b-4359-bdb9-76c166a2603d"// **optional**, specify which terminal should query,default query data on all terminal
}
```
- Response data specification:
```json
{
  "status": 0,
  "data": {
    "traffic_count": 1
  }
}
```


### 2. Query Truck traffic history group by truck type
- Endpoint: **GET** /api/query-truck-type-traffics/
- Request data specification: **None**
- Response data specification:
```json
{
  "status": 0,
  "data": [
    {
      "Truck Type": "Caminhão 3/4",
      "Origin Terminal": "Taubaté",
      "Destination Terminal": "Tietê"
    },
    {
      "Truck Type": "Caminhão 3/4",
      "Origin Terminal": "Tietê",
      "Destination Terminal": "Taubaté"
    }
  ]
}
```


### 7. Update driver register information
- Endpoint: **PUT** /api/update-driver-info/
- Request data specification:
```json
{
  "cpf_no": "23725897840",// **required**, identify driver
  "name": "Liang", // **optional**
  "age": 30, // **optional**
  "gender": 1, // **optional**
  "drive_license_type": "A/B", // **optional**
  "has_truck": true, // **optional**
  "is_loaded": false, // **optional**
  "from_terminal": "35ff14e0-664d-43c6-abad-e68ac8b61809", // **optional**
  "to_terminal": "4c91204e-f63b-4359-bdb9-76c166a2603d" // **optional**
}
```

- Response data specification:
```json
{
  "status": 0,
  "data": {
    "object_id": "59f3e8bf-74f6-4b95-b1c9-6f0e6b86ce53",
    "created_at": 1545005672,
    "updated_at": 1545009878,
    "cpf_no": "23725897840",
    "name": "Liang",
    "age": 30,
    "gender": 1,
    "drive_license_type": "A/B",
    "has_truck": true,
    "from_terminal": "35ff14e0-664d-43c6-abad-e68ac8b61809",
    "to_terminal": "4c91204e-f63b-4359-bdb9-76c166a2603d"
  }
}
```



