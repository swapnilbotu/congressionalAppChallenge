tasks = ""
i = 0
Dwas= [
        {
          "DwaTitle": "Prepare documentation for contracts, transactions, or regulatory compliance.",
          "DwaId": "4.A.3.b.6.I13.D05",
          "DataValue": "4.62",
          "TaskId": "23240"
        },
        {
          "DwaTitle": "Operate office equipment.",
          "DwaId": "4.A.3.a.3.I01.D01",
          "DataValue": "4.48",
          "TaskId": "23242"
        },
        {
          "DwaTitle": "Verify accuracy of financial or transactional data.",
          "DwaId": "4.A.2.a.2.I01.D09",
          "DataValue": "4.86",
          "TaskId": "23238"
        },
        {
          "DwaTitle": "Maintain financial or account records.",
          "DwaId": "4.A.3.b.6.I10.D03",
          "DataValue": "4.35",
          "TaskId": "23241"
        },
        {
          "DwaTitle": "Route mail to correct destinations.",
          "DwaId": "4.A.4.c.1.I05.D04",
          "DataValue": "3.86",
          "TaskId": "23247"
        },
        {
          "DwaTitle": "Monitor equipment operation to ensure proper functioning.",
          "DwaId": "4.A.1.a.2.I01.D05",
          "DataValue": "3.51",
          "TaskId": "23248"
        },
        {
          "DwaTitle": "Calculate costs of goods or services.",
          "DwaId": "4.A.2.b.1.I01.D07",
          "DataValue": "4.46",
          "TaskId": "23245"
        },
        {
          "DwaTitle": "Maintain operational records.",
          "DwaId": "4.A.3.b.6.I08.D05",
          "DataValue": "4.33",
          "TaskId": "23256"
        },
        {
          "DwaTitle": "Weigh parcels to determine shipping costs.",
          "DwaId": "4.A.1.b.3.I01.D13",
          "DataValue": "4.23",
          "TaskId": "23250"
        }]
for i in range(10):
    dwa = Dwas[i]
    task = dwa.get("DwaTitle")
    tasks += task