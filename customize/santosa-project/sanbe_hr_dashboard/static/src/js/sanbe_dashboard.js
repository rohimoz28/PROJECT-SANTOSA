/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, onWillStart, onWillUnmount, useState, onWillUpdateProps } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { ChartRenderer } from "./chart_renderer"; // Updated import path

// import { Chart } from "chart.js/auto";

class SalesDashboardComponent extends Component {
    setup() {
        this.orm = useService("orm");
            this.state = useState({
                total_employees: 0,
                employees: [],
                resignation_count: [],
                employee_count: [],
                currentMonth: new Date().toLocaleString('default', { month: 'short' }), // Format "Jan", "Feb", dll.
                selectedMonth: new Date().toLocaleString('default', { month: 'short' }),
                currentMonth2: new Date().toLocaleString('default', { month: 'short' }), // Format "Jan", "Feb", dll.
                selectedMonth2: new Date().toLocaleString('default', { month: 'short' }),
                months: [
                    'Januari', 'Februari', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
                ],
                categories: [],
                isLoading: false,
                //currentMonth: new Date().toLocaleString('default', { month: 'long' }),
                lastMonth: new Date(new Date().setMonth(new Date().getMonth() - 1)).toLocaleString('default', { month: 'long' }),
                resignationData: {},
                chartKey: 0, 
                chartData: {
                    labels: [],
                    datasets: []
                },
                chartData2: {
                    labels: [],
                    datasets: []
                }
            });
            onWillStart(async () => {
                await this.fetchData();
                await this.fetchData2();
                this.state.chartKey += 1;
                // await this.getMonth()
            });
    
            onWillUnmount(() => {
                clearInterval(this.pollingInterval); 
            });

          
        }

        onChangePeriod(event) {
            const selectedFilter = event.target.value; 
            this.fetchData(selectedFilter); // Load vehicle data with the selected filter
            // this.willUpdateProps();
        }   
        onChangePeriod2(event) {
            const selectedFilter = event.target.value; 
            this.fetchData2(selectedFilter); // Load vehicle data with the selected filter
            // this.willUpdateProps();
        }

    async fetchData(filterType) {
        try {
            const monthsMap = {
                Jan: 'Jan',
                Feb: 'Feb',
                Mar: 'Mar',
                Apr: 'Apr',
                May: 'May',
                Jun: 'Jun',
                Jul: 'Jul',
                Aug: 'Aug',
                Sep: 'Sep',
                Oct: 'Oct',
                Nov: 'Nov',
                Dec: 'Dec',
            };

            const months = [
                "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
            ];
            
            
            
            const currentMonth = new Date().toLocaleString('default', { month: 'short' }); // Bulan saat ini (panjang)
            // const lastMonth = new Date(new Date().setMonth(new Date().getMonth() - 1)).toLocaleString('default', { month: 'short' });
            const selectedMonth = this.state.selectedMonth || "current"; // Mengambil bulan yang dipilih atau default ke 'current'
            const selectedMonthIndex = months.indexOf(selectedMonth);
            const lastMonthIndex = (selectedMonthIndex - 1 + 12) % 12;
            
            // Ambil nama bulan sebelumnya
            const lastMonth = months[lastMonthIndex];

            console.log(`Selected Month: ${selectedMonth}`);
            console.log(`Last Month: ${lastMonth}`);
            
            const displayMonth = selectedMonth === new Date().toLocaleString('default', { month: 'short' }) 
                ? currentMonth 
                : monthsMap[selectedMonth] || selectedMonth; 
            
            this.state.currentMonth = ` - ${displayMonth}`;

            if (lastMonth) {
                // Gunakan kunci sesuai case di monthsMap
                const displayLastMonth = monthsMap[lastMonth] || lastMonth;
            
                console.log(`Last Month: ${displayLastMonth}`);
            
                this.state.lastMonth = ` - ${displayLastMonth}`;
            } else {
                console.error("lastMonth is not defined or invalid");
                this.state.lastMonth = " - Unknown Month";
            }

            const categories = [
                'End Of Contract', 'Resign', 'Transfer To Group', 'Pension', 'Terminate'
            ];
            this.state.categories = categories;

            // console.log("NIH YA LIAT:", displayMonth);

            // this.state.currentMonth = ` - ${displayMonth}`;

            const employees = await this.orm.searchRead(
                "hr.employee",
                [],
                ["name", "job_title", "marital"]
            ).catch(error => {
                console.error("Error fetching employees:", error);
                return [];
            });

            // Fetch dashboard data
            const dashboardData = await this.orm.call(
                "hr.resignation",
                "get_dashboard_data",
                []
            ).catch(error => {
                console.error("Error fetching dashboard data:", error);
                return { resignation_data: [], end_contract_data: [], transfer_to_group: [], terminate_data: [], pension_data: [] };
            });
            // console.log("Dashboard data:", dashboardData);
        
                // Areas
                const areas = ['Taman Sari', 'Cimahi', 'Cimareme'];

                // Prepare result structure
                const employeeExitData = {
                    lastMonth: {},
                    currentMonth: {},
                    lastMonthTotals: {},
                    currentMonthTotals: {}
                };
                
                // Initialize area totals
                areas.forEach(area => {
                    employeeExitData.lastMonthTotals[area] = 0;
                    employeeExitData.currentMonthTotals[area] = 0;
                });
                
                // Process data for each category and area
                categories.forEach(category => {
                    // Pastikan struktur data kategori terdefinisi
                    employeeExitData.lastMonth[category] = {};
                    employeeExitData.currentMonth[category] = {};
                
                    areas.forEach(area => {
                        // Dapatkan array data yang relevan berdasarkan kategori
                        let dataArray = [];
                        switch (category) {
                            case 'Resign':
                                dataArray = dashboardData.resignation_data || [];
                                break;
                            case 'End Of Contract':
                                dataArray = dashboardData.end_contract_data || [];
                                break;
                            case 'Transfer To Group':
                                dataArray = dashboardData.transfer_to_group || [];
                                break;
                            case 'Terminate':
                                dataArray = dashboardData.terminate_data || [];
                                break;
                            case 'Pension':
                                dataArray = dashboardData.pension_data || [];
                                break;
                            default:
                                console.error(`Unknown category: ${category}`);
                        }
                
                        // Filter dan hitung untuk bulan sebelumnya
                        const lastMonthData = dataArray.filter(item =>
                            item.month === lastMonth && item.areas === area
                        );
                        const lastMonthCount = lastMonthData.length > 0
                            ? lastMonthData[0].resignation_count
                            : 0;
                        employeeExitData.lastMonth[category][area] = lastMonthCount;
                
                        // Tambahkan ke total area untuk bulan sebelumnya
                        if (!employeeExitData.lastMonthTotals[area]) {
                            employeeExitData.lastMonthTotals[area] = 0;
                        }
                        employeeExitData.lastMonthTotals[area] += lastMonthCount;
                
                        // Filter dan hitung untuk bulan saat ini
                        const currentMonthData = dataArray.filter(item =>
                            item.month === selectedMonth && item.areas === area
                        );
                        const currentMonthCount = currentMonthData.length > 0
                            ? currentMonthData[0].resignation_count
                            : 0;
                        employeeExitData.currentMonth[category][area] = currentMonthCount;
                
                        // Tambahkan ke total area untuk bulan saat ini
                        if (!employeeExitData.currentMonthTotals[area]) {
                            employeeExitData.currentMonthTotals[area] = 0;
                        }
                        employeeExitData.currentMonthTotals[area] += currentMonthCount;
                    });
                });
                
                // Store in state for template rendering
                this.state.employeeExitData = employeeExitData;
                
                console.log("Employee Exit Data:", employeeExitData);
        


            // Filter the data based on the selected month
            const filterByMonth = (data) => {
                const filteredData = data.filter(item => {
                    if (!item.month) return false;
                    return item.month === selectedMonth || selectedMonth === "current";
                });
                console.log("Filtered data for month:", selectedMonth, filteredData);
                return filteredData;
            };
            

            const resignation_data = filterByMonth(dashboardData?.resignation_data || []);
            const end_contract_data = filterByMonth(dashboardData?.end_contract_data || []);
            const transfer_to_group = filterByMonth(dashboardData?.transfer_to_group || []);
            const terminate_data = filterByMonth(dashboardData?.terminate_data || []);
            const pension_data = filterByMonth(dashboardData?.pension_data || []);

            // console.log("DATA RESIGN:", resignation_data);

       
            const validResignationData = resignation_data.filter(data => data.areas);
            const validEndContractData = end_contract_data.filter(data => data.areas);
            const validTransferGroupData = transfer_to_group.filter(data => data.areas);
            const validTerminateData = terminate_data.filter(data => data.areas);
            const validPensionData = pension_data.filter(data => data.areas);

            // console.log("VALID RESIGN:", resignation_data);

          
            this.state.total_employees = employees.length;
            this.state.employees = employees;

            // Prepare chart labels and datasets
            const labels = [...new Set([...validResignationData.map(d => d.areas ).filter(area => area),
                ...validEndContractData.map(d => d.areas),
                ...validTransferGroupData.map(d => d.areas),
                ...validTerminateData.map(d => d.areas),
                ...validPensionData.map(d => d.areas)
            ])];

            const datasets = [
                {
                    label: 'Resignations',
                    data: labels.map(label => {
                        const currentMonth = new Date().toLocaleString('default', { month: 'long' });
                        const selectedMonth = this.state.selectedMonth;
                        const displayMonth = selectedMonth === "current" ? currentMonth : selectedMonth;
                        // console.log("YUUU BISA YUUU:", displayMonth);
                        const data = validResignationData.find(d => d.areas === label && d.month === displayMonth);
                        // console.log("YUUU BISA YUUU 2:", displayMonth);
                        // console.log("Resignation Data for label:", label, data);
                        return data ? data.resignation_count : 0;
                    }),
                    date: (() => {
                        const monthMap = {
                            'Jan':  ['01', '31'],
                            'Feb':  ['02', '28'], // Note: Adjust for leap years if needed
                            'Mar':  ['03', '31'],
                            'Apr':  ['04', '30'],
                            'May':  ['05', '31'],
                            'Jun':  ['06', '30'],
                            'Jul':  ['07', '31'],
                            'Aug':  ['08', '31'],
                            'Sep':  ['09', '30'],
                            'Oct':  ['10', '31'],
                            'Nov':  ['11', '30'],
                            'Dec':  ['12', '31']
                        };
                        
                        const currentYear = new Date().getFullYear();
        const monthData = monthMap[displayMonth];
        
        return monthData 
            ? [`${currentYear}-${monthData[0]}-01`, `${currentYear}-${monthData[0]}-${monthData[1]}`]
            : [`${currentYear}-01-01`];
    })(),
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                },
                {
                    label: 'End of Contracts',
                    data: labels.map(label => {
                        const currentMonth = new Date().toLocaleString('default', { month: 'long' });
                        const selectedMonth = this.state.selectedMonth;
                        const displayMonth = selectedMonth === "current" ? currentMonth : selectedMonth;
                        const data = validEndContractData.find(d => d.areas === label && d.month === displayMonth
                        ) ;
                        // console.log("Data EOC:", data);
                        return data ? data.resignation_count : 0;
                        
                    }),
                    date: (() => {
                        const monthMap = {
                            'Jan':  ['01', '31'],
                            'Feb':  ['02', '28'], // Note: Adjust for leap years if needed
                            'Mar':  ['03', '31'],
                            'Apr':  ['04', '30'],
                            'May':  ['05', '31'],
                            'Jun':  ['06', '30'],
                            'Jul':  ['07', '31'],
                            'Aug':  ['08', '31'],
                            'Sep':  ['09', '30'],
                            'Oct':  ['10', '31'],
                            'Nov':  ['11', '30'],
                            'Dec':  ['12', '31']
                        };
                        
                        const currentYear = new Date().getFullYear();
        const monthData = monthMap[displayMonth];
        
        return monthData 
            ? [`${currentYear}-${monthData[0]}-01`, `${currentYear}-${monthData[0]}-${monthData[1]}`]
            : [`${currentYear}-01-01`];
    })(),
                    backgroundColor: 'rgba(255, 99, 132, 0.6)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1,
                },
                {
                    label: 'Transfer To Group',
                    data: labels.map(label => {
                        const currentMonth = new Date().toLocaleString('default', { month: 'long' });
                        const selectedMonth = this.state.selectedMonth;
                        const displayMonth = selectedMonth === "current" ? currentMonth : selectedMonth;
                        const data = validTransferGroupData.find(d => d.areas === label && d.month === displayMonth);
                        return data ? data.resignation_count : 0;
                    }),
                    date: (() => {
                        const monthMap = {
                            'Jan':  ['01', '31'],
                            'Feb':  ['02', '28'], // Note: Adjust for leap years if needed
                            'Mar':  ['03', '31'],
                            'Apr':  ['04', '30'],
                            'May':  ['05', '31'],
                            'Jun':  ['06', '30'],
                            'Jul':  ['07', '31'],
                            'Aug':  ['08', '31'],
                            'Sep':  ['09', '30'],
                            'Oct':  ['10', '31'],
                            'Nov':  ['11', '30'],
                            'Dec':  ['12', '31']
                        };
                        
                        const currentYear = new Date().getFullYear();
        const monthData = monthMap[displayMonth];
        
        return monthData 
            ? [`${currentYear}-${monthData[0]}-01`, `${currentYear}-${monthData[0]}-${monthData[1]}`]
            : [`${currentYear}-01-01`];
    })(),
                    backgroundColor: 'rgba(160, 160, 160, 0.6)',
                    borderColor: 'rgba(160, 160, 160, 1)',
                    borderWidth: 1,
                },
                {
                    label: 'Terminate',
                    data: labels.map(label => {
                        const currentMonth = new Date().toLocaleString('default', { month: 'long' });
                        const selectedMonth = this.state.selectedMonth;
                        const displayMonth = selectedMonth === "current" ? currentMonth : selectedMonth;
                        const data = validTerminateData.find(d => d.areas === label && d.month === displayMonth);
                        return data ? data.resignation_count : 0;
                    }),
                    date: (() => {
                        const monthMap = {
                            'Jan':  ['01', '31'],
                            'Feb':  ['02', '28'], // Note: Adjust for leap years if needed
                            'Mar':  ['03', '31'],
                            'Apr':  ['04', '30'],
                            'May':  ['05', '31'],
                            'Jun':  ['06', '30'],
                            'Jul':  ['07', '31'],
                            'Aug':  ['08', '31'],
                            'Sep':  ['09', '30'],
                            'Oct':  ['10', '31'],
                            'Nov':  ['11', '30'],
                            'Dec':  ['12', '31']
                        };
                        
                        const currentYear = new Date().getFullYear();
        const monthData = monthMap[displayMonth];
        
        return monthData 
            ? [`${currentYear}-${monthData[0]}-01`, `${currentYear}-${monthData[0]}-${monthData[1]}`]
            : [`${currentYear}-01-01`];
    })(),
                    backgroundColor: 'rgba(255, 255, 0, 0.6)',
                    borderColor: 'rgba(255, 255, 0, 1)',
                    borderWidth: 1,
                },
                {
                    label: 'Pension',
                    data: labels.map(label => {
                        const currentMonth = new Date().toLocaleString('default', { month: 'long' });
                        const selectedMonth = this.state.selectedMonth;
                        const displayMonth = selectedMonth === "current" ? currentMonth : selectedMonth;
                        const data = validPensionData.find(d => d.areas === label && d.month === displayMonth);
                        return data ? data.resignation_count : 0;
                    }),
                    date: (() => {
                        const monthMap = {
                            'Jan':  ['01', '31'],
                            'Feb':  ['02', '28'], // Note: Adjust for leap years if needed
                            'Mar':  ['03', '31'],
                            'Apr':  ['04', '30'],
                            'May':  ['05', '31'],
                            'Jun':  ['06', '30'],
                            'Jul':  ['07', '31'],
                            'Aug':  ['08', '31'],
                            'Sep':  ['09', '30'],
                            'Oct':  ['10', '31'],
                            'Nov':  ['11', '30'],
                            'Dec':  ['12', '31']
                        };
                        
                        const currentYear = new Date().getFullYear();
        const monthData = monthMap[displayMonth];
        
        return monthData 
            ? [`${currentYear}-${monthData[0]}-01`, `${currentYear}-${monthData[0]}-${monthData[1]}`]
            : [`${currentYear}-01-01`];
    })(),
                    backgroundColor: 'rgba(0, 128, 255, 0.6)',
                    borderColor: 'rgba(0, 128, 255, 1)',
                    borderWidth: 1,
                }
            ];
            
            

            this.state.chartData = { labels, datasets };
           
            // console.log("Updateddddddd:", this.state.chartData);

            // this.renderChart();
        } catch (error) {
            console.error("Error in fetchData:", error);
            // Default fallback for errors
            this.state.chartData = {
                labels: [],
                datasets: [
                    {
                        label: 'Resignations',
                        data: [],
                        backgroundColor: 'rgba(75, 192, 192, 0.6)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1,
                    },
                    {
                        label: 'End of Contracts',
                        data: [],
                        backgroundColor: 'rgba(255, 99, 132, 0.6)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1,
                    },
                    {
                        label: 'Transfer To Group',
                        data: [],
                        backgroundColor: 'rgba(160, 160, 160, 0.6)',
                        borderColor: 'rgba(160, 160, 160, 1)',
                        borderWidth: 1,
                    },
                    {
                        label: 'Terminate',
                        data: [],
                        backgroundColor: 'rgba(255, 255, 0, 0.6)',
                        borderColor: 'rgba(255, 255, 0, 1)',
                        borderWidth: 1,
                    },
                    {
                        label: 'Pension',
                        data: [],
                        backgroundColor: 'rgba(0, 128, 255, 0.6)',
                        borderColor: 'rgba(0, 128, 255, 1)',
                        borderWidth: 1,
                    }
                ]
            };
        }
    }

    async fetchData2(filterType) {
        try {
            const monthsMap = {
                Jan: 'Jan',
                Feb: 'Feb',
                Mar: 'Mar',
                Apr: 'Apr',
                May: 'May',
                Jun: 'Jun',
                Jul: 'Jul',
                Aug: 'Aug',
                Sep: 'Sep',
                Oct: 'Oct',
                Nov: 'Nov',
                Dec: 'Dec',
            };

            const months = [
                "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
            ];
            
            
            
            const currentMonth2 = new Date().toLocaleString('default', { month: 'short' });
           // const lastMonth = new Date(new Date().setMonth(new Date().getMonth() - 1)).toLocaleString('default', { month: 'short' });
            const selectedMonth2 = this.state.selectedMonth2 || new Date().toLocaleString('default', { month: 'long' });;
            const selectedMonthIndex = months.indexOf(selectedMonth2);
            const lastMonthIndex = (selectedMonthIndex - 1 + 12) % 12;
            
            // Ambil nama bulan sebelumnya
            const lastMonth = months[lastMonthIndex];
            
            console.log(`Selected Month: ${selectedMonth2}`);
            console.log(`Last Month: ${lastMonth}`);
            
            const displayMonth = selectedMonth2 === new Date().toLocaleString('default', { month: 'short' })  
                ? currentMonth2 
                : monthsMap[selectedMonth2] || selectedMonth2; // Mapping untuk nama panjang
            
            this.state.currentMonth2 = ` - ${displayMonth}`;

            if (lastMonth) {
                // Gunakan kunci sesuai case di monthsMap
                const displayLastMonth2 = monthsMap[lastMonth] || lastMonth;
            
                console.log(`Last Month: ${displayLastMonth2}`);
            
                this.state.lastMonth2 = ` - ${displayLastMonth2}`;
            } else {
                console.error("lastMonth is not defined or invalid");
                this.state.lastMonth2 = " - Unknown Month";
            }

            const categories = [
                'Active Employee', 'Employee Exit', 'New Employee'
            ];
            this.state.categories2 = categories;

            // console.log("NIH YA LIAT:", displayMonth);

            // this.state.currentMonth = ` - ${displayMonth}`;

            const employees = await this.orm.searchRead(
                "hr.employee",
                [],
                ["name", "job_title", "marital"]
            ).catch(error => {
                console.error("Error fetching employees:", error);
                return [];
            });

            // Fetch dashboard data
            const dashboardData = await this.orm.call(
                "hr.resignation",
                "get_employee_data",
                []
            ).catch(error => {
                console.error("Error fetching dashboard data:", error);
                return { employee_active_data: [], employee_exit_data: [], employee_new_data: [] };
            });
            // console.log("Dashboard data:", dashboardData);
        
                // Areas
                const areas = ['Taman Sari', 'Cimahi', 'Cimareme'];

                // // Prepare result structure
                const employeeHeadCountData = {
                    lastMonth: {},
                    currentMonth: {},
                    lastMonthTotals: {},
                    currentMonthTotals: {}
                };
                
                // // Initialize area totals
                areas.forEach(area => {
                    employeeHeadCountData.lastMonthTotals[area] = 0;
                    employeeHeadCountData.currentMonthTotals[area] = 0;
                });
                
                // // Process data for each category and area
                categories.forEach(category => {
                    employeeHeadCountData.lastMonth[category] = {};
                    employeeHeadCountData.currentMonth[category] = {};
                
                    areas.forEach(area => {
                        // Determine the correct data array based on category
                        let dataArray;
                        switch(category) {
                            case 'Active Employee':
                                dataArray = dashboardData.employee_active_data;
                                break;
                            case 'New Employee':
                                dataArray = dashboardData.employee_new_data;
                                break;
                            case 'Employee Exit':
                                dataArray = dashboardData.employee_exit_data;
                                break;

                        }
                
                        // Filter and count for last month
                        const lastMonthData = dataArray.filter(item => 
                            item.month === lastMonth && item.areas === area
                        );
                        console.log("data array:", lastMonthData);
                        const lastMonthCount = lastMonthData.length > 0 
                            ? lastMonthData[0].employee_count 
                            : 0;
                        employeeHeadCountData.lastMonth[category][area] = lastMonthCount;
                        
                        // Add to area total for last month
                        employeeHeadCountData.lastMonthTotals[area] += lastMonthCount;
                
                        // Filter and count for current month
                        const currentMonthData = dataArray.filter(item => 
                            item.month === selectedMonth2 && item.areas === area
                        );
                        const currentMonthCount = currentMonthData.length > 0 
                            ? currentMonthData[0].employee_count 
                            : 0;
                        employeeHeadCountData.currentMonth[category][area] = currentMonthCount;
                        
                        // Add to area total for current month
                        employeeHeadCountData.currentMonthTotals[area] += currentMonthCount;
                    });
                });
                
                // // Store in state for template rendering
                this.state.employeeHeadCountData = employeeHeadCountData;
                
                console.log("Employee Count Data:", employeeHeadCountData);
        


            // Filter the data based on the selected month
            const filterByMonth = (data) => {
                const filteredData = data.filter(item => {
                    if (!item.month) return false;
                    return item.month === selectedMonth2 || selectedMonth2 === "current";
                });
                console.log("Filtered data for month:", selectedMonth2, filteredData);
                return filteredData;
            };
            

            const employee_active_data = filterByMonth(dashboardData?.employee_active_data || []);
            const employee_new_data = filterByMonth(dashboardData?.employee_new_data || []);
            const employee_exit_data = filterByMonth(dashboardData?.employee_exit_data || []);

            // console.log("DATA RESIGN:", resignation_data);

       
            const validEmployeeActiveData = employee_active_data.filter(data => data.areas);
            const validEmployeeNewData = employee_new_data.filter(data => data.areas);
            const validEmployeeExitData = employee_exit_data.filter(data => data.areas);

            // console.log("VALID RESIGN:", resignation_data);

          
            this.state.total_employees = employees.length;
            this.state.employees = employees;

            // Prepare chart labels and datasets
            const labels = [...new Set([...validEmployeeActiveData.map(d => d.areas ).filter(area => area),
                ...validEmployeeNewData.map(d => d.areas),
                ...validEmployeeExitData.map(d => d.areas)
            ])];

            const datasets = [
                {
                    label: 'Active Employee',
                    data: labels.map(label => {
                        const currentMonth = new Date().toLocaleString('default', { month: 'short' });
                        const selectedMonth2 = this.state.selectedMonth2;
                        const displayMonth = selectedMonth2 === "current" ? currentMonth : selectedMonth2;
                        // console.log("YUUU BISA YUUU:", displayMonth);
                        const data = validEmployeeActiveData.find(d => d.areas === label && d.month === displayMonth);
                        // console.log("YUUU BISA YUUU 2:", displayMonth);
                        // console.log("Resignation Data for label:", label, data);
                        return data ? data.employee_count : 0;
                    }),
                    date: (() => {
                        const monthMap = {
                            'Jan':  ['01', '31'],
                            'Feb':  ['02', '28'], 
                            'Mar':  ['03', '31'],
                            'Apr':  ['04', '30'],
                            'May':  ['05', '31'],
                            'Jun':  ['06', '30'],
                            'Jul':  ['07', '31'],
                            'Aug':  ['08', '31'],
                            'Sep':  ['09', '30'],
                            'Oct':  ['10', '31'],
                            'Nov':  ['11', '30'],
                            'Dec':  ['12', '31']
                        };
                        
                        const currentYear = new Date().getFullYear();
                        const monthData = monthMap[displayMonth];

        console.log("cek bulan:", monthData);
        console.log("cek bulan 2:", displayMonth);
        
        return monthData 
            ? [`${currentYear}-${monthData[0]}-01`, `${currentYear}-${monthData[0]}-${monthData[1]}`]
            : [`${currentYear}-01-01`];
    })(),
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                },
                {
                    label: 'Employee Exit',
                    data: labels.map(label => {
                        const currentMonth = new Date().toLocaleString('default', { month: 'long' });
                        const selectedMonth2 = this.state.selectedMonth2;
                        const displayMonth = selectedMonth2 === "current" ? currentMonth : selectedMonth2;
                        const data = validEmployeeExitData.find(d => d.areas === label && d.month === displayMonth
                        ) ;
                        // console.log("Data EOC:", data);
                        return data ? data.employee_count : 0;
                        
                    }),
                    date: (() => {
                        const monthMap = {
                            'Jan':  ['01', '31'],
                            'Feb':  ['02', '28'], 
                            'Mar':  ['03', '31'],
                            'Apr':  ['04', '30'],
                            'May':  ['05', '31'],
                            'Jun':  ['06', '30'],
                            'Jul':  ['07', '31'],
                            'Aug':  ['08', '31'],
                            'Sep':  ['09', '30'],
                            'Oct':  ['10', '31'],
                            'Nov':  ['11', '30'],
                            'Dec':  ['12', '31']
                        };
                        
                        const currentYear = new Date().getFullYear();
        const monthData = monthMap[displayMonth];
        
        return monthData 
            ? [`${currentYear}-${monthData[0]}-01`, `${currentYear}-${monthData[0]}-${monthData[1]}`]
            : [`${currentYear}-01-01`];
    })(),
                    backgroundColor: 'rgba(255, 99, 132, 0.6)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1,
                },
                {
                    label: 'New Employee',
                    data: labels.map(label => {
                        const currentMonth = new Date().toLocaleString('default', { month: 'long' });
                        const selectedMonth2 = this.state.selectedMonth2;
                        const displayMonth = selectedMonth2 === "current" ? currentMonth : selectedMonth2;
                        const data = validEmployeeNewData.find(d => d.areas === label && d.month === displayMonth);
                        return data ? data.employee_count : 0;
                        
                    }),
                    date: (() => {
                        const monthMap = {
                            'Jan':  ['01', '31'],
                            'Feb':  ['02', '28'], 
                            'Mar':  ['03', '31'],
                            'Apr':  ['04', '30'],
                            'May':  ['05', '31'],
                            'Jun':  ['06', '30'],
                            'Jul':  ['07', '31'],
                            'Aug':  ['08', '31'],
                            'Sep':  ['09', '30'],
                            'Oct':  ['10', '31'],
                            'Nov':  ['11', '30'],
                            'Dec':  ['12', '31']
                        };
                        
                        const currentYear = new Date().getFullYear();
        const monthData = monthMap[displayMonth];
        
        return monthData 
            ? [`${currentYear}-${monthData[0]}-01`, `${currentYear}-${monthData[0]}-${monthData[1]}`]
            : [`${currentYear}-01-01`];
    })(),
                    backgroundColor: 'rgba(160, 160, 160, 0.6)',
                    borderColor: 'rgba(160, 160, 160, 1)',
                    borderWidth: 1,
                }
                
            ];
           
            

            this.state.chartData2 = { labels, datasets };
            console.log("cek data get nya:", datasets);
           
            // console.log("Updateddddddd:", this.state.chartData);

        } catch (error) {
            console.error("Error in fetchData:", error);
            // Default fallback for errors
            this.state.chartData2 = {
                labels: [],
                datasets: [
                    {
                        label: 'Active Employee',
                        data: [],
                        backgroundColor: 'rgba(75, 192, 192, 0.6)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1,
                    },
                    {
                        label: 'Employee Exit',
                        data: [],
                        backgroundColor: 'rgba(255, 99, 132, 0.6)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1,
                    },
                    {
                        label: 'New Employee',
                        data: [],
                        backgroundColor: 'rgba(160, 160, 160, 0.6)',
                        borderColor: 'rgba(160, 160, 160, 1)',
                        borderWidth: 1,
                    },
                    
                ]
            };
        }
        
    }



    willUpdateProps(nextProps) {
    
        // Validasi data baru
        if (!this.isValidChartData(nextProps.data)) {
            // Render ulang jika data tidak valid
            this.renderChart();
            return;
        }
    
        // Perbarui chart jika data valid
        if (this.chart && nextProps.data) {
            this.chart.data = nextProps.data;
            this.chart.update();
        }
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('id-ID', {
            style: 'currency',
            currency: 'IDR',
            minimumFractionDigits: 0
        }).format(amount);
    }

}


SalesDashboardComponent.template = "sanbe_hr_dashboard.SalesDashboardField";
SalesDashboardComponent.components = { ChartRenderer }

registry.category("actions").add("backend_dashboard", SalesDashboardComponent);



