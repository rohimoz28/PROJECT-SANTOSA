/** @odoo-module **/
import { registry } from "@web/core/registry";
import { loadJS } from "@web/core/assets";
import { Component, onWillStart, onMounted, useEffect, onWillUnmount, useRef } from "@odoo/owl";

export class ChartRenderer extends Component {
    setup() {
        this.chartRef = useRef("chart");
        this.chart = null;

        // Load Chart.js library
        onWillStart(async () => {
            await loadJS("/web/static/lib/Chart/Chart.js");
            // await loadJS("/web/static/lib/chartjs-plugin-annotation/chartjs-plugin-annotation.min.js");
        });

        // Render chart after component is mounted
        onMounted(() => {
            this.renderChart();
        });

        // Re-render chart whenever `data` or `type` props change
        useEffect(() => {
            this.renderChart();
            // this._onChartClick();
        }, () => [this.props.data, this.props.type]);

        // Destroy the chart when the component is unmounted
        onWillUnmount(() => {
            if (this.chart) {
                this.chart.destroy();
            }
        });
    }

    // renderChart() {
    //     // Destroy the existing chart to avoid duplication
    //     if (this.chart) {
    //         this.chart.destroy();
    //     }

    //     // Get the chart data and options
    //     const data = this.props.data || {
    //         labels: [],
    //         datasets: []
    //     };

    //     this.chart = new Chart(this.chartRef.el, {
    //         type: this.props.type || 'bar',
    //         data: data,
    //         options: {
    //             onClick: (event, elements, chart) => this._onChartClick(event, elements, chart),
    //             responsive: true,
    //             maintainAspectRatio: false,
    //             hover: {
    //                 cursor: 'pointer'
    //             },
    //             onHover: (event, chartElement) => {
    //                 event.native.target.style.cursor = chartElement[0] ? 'pointer' : 'default';
    //             },
    //             plugins: {
    //                 legend: {
    //                     position: 'bottom',
    //                 },
    //                 title: {
    //                     display: true,
    //                     text: this.props.title || '',
    //                 },
    //                 datalabels: {
    //                     anchor: "end",
    //                     align: "top",
    //                     formatter: (value) => data, // Menampilkan nilai data
    //                     font: {
    //                         weight: "bold",
    //                     },
    //                 }
    //             },
    //             scales: {
    //                 y: {
    //                     beginAtZero: true,
    //                     ticks: {
    //                         precision: 0
    //                     }
    //                 }
    //             }
    //             // onClick: this.props.onClick || (() => {})
    //         },
    //     });
    // }
    renderChart() {
        // Destroy the existing chart to avoid duplication
        if (this.chart) {
            this.chart.destroy();
        }
    
        // Get the chart data and options
        const data = this.props.data || {
            labels: [],
            datasets: [],
        };
    
        this.chart = new Chart(this.chartRef.el, {
            type: this.props.type || "bar",
            data: data,
            options: {
                onClick: (event, elements, chart) => this._onChartClick(event, elements, chart),
                responsive: true,
                maintainAspectRatio: false,
                hover: {
                    cursor: 'pointer'
                 },
                onHover: (event, chartElement) => {
                    event.native.target.style.cursor = chartElement[0] ? 'pointer' : 'default';
                },
                plugins: {
                    legend: {
                        position: "bottom",
                    },
                    title: {
                        display: true,
                        text: this.props.title || "",
                    },
                    datalabels: {
                        anchor: "end",
                        align: "top",
                        formatter: (value) => value, // Menampilkan nilai data
                        font: {
                            weight: "bold",
                        },
                    },
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0,
                        },
                    },
                },
            },
            plugins: [
                {
                    id: "custom-datalabels",
                    afterDatasetsDraw: (chart) => {
                        const { ctx } = chart;
                        chart.data.datasets.forEach((dataset, datasetIndex) => {
                            const meta = chart.getDatasetMeta(datasetIndex);
                            meta.data.forEach((bar, index) => {
                                const value = dataset.data[index];
                                ctx.fillStyle = "#000"; // Warna teks
                                ctx.font = "12px Arial";
                                ctx.fillText(
                                    value,
                                    bar.x - 10,
                                    bar.y - 10 // Posisi teks di atas batang
                                );
                            });
                        });
                    },
                },
            ],
        });
    }
    

    _onChartClick(event, elements, chart) {
        if (Array.isArray(elements) && elements.length > 0) {
            const clickedIndex = elements[0].index;
            const areaName = chart.data.labels[clickedIndex];
            const clickedDatasetLabel = chart.data.datasets[elements[0].datasetIndex].label;
            const clickedDataset = chart.data.datasets[elements[0].datasetIndex];
    
            console.log("cek data:", clickedIndex);  
            console.log("cek tanggal:", clickedDataset);
    
            let domain = [];
            let context = {};
            const categoryMapping = {
                'Resignations': 'Resign',
                'End of Contracts': 'End Of Contract',
                'Transfer To Group': 'Transfer To Group',
                'Terminate': 'Terminate',
                'Pension': 'Pension',
                'Active Employee': 'Active Employee',
                'Employee Exit': 'Employee Exit',
                'New Employee': 'New Employee',
            };
    
            const category = categoryMapping[clickedDatasetLabel] || '';
            console.log("cek data kategori:", category);
            switch(true) {
                case areaName === 'Taman Sari' && category === 'Active Employee' :
                    domain = [
                        ["area", "=", 1],
                        ["emp_status", "in", ["probation", "confirmed"]]
                    ];
                    break;
                case areaName === 'Cimareme' && category === 'Active Employee' :
                    domain = [
                        ["area", "=", 3],
                        ["emp_status", "in", ["probation", "confirmed"]]
                    ];
                    break;
                case areaName === 'Cimahi' && category === 'Active Employee' :
                    domain = [
                        ["area", "=", 2],
                        ["emp_status", "in", ["probation", "confirmed"]]
                    ];
                    break;
                case areaName === 'Taman Sari' && category === 'New Employee' :
                        domain = [
                            ["area", "=", 1],
                            ["emp_status", "in", ["probation", "confirmed"]],
                             "&",
                                ["join_date", ">=",  clickedDataset.date[0]], 
                                ["join_date", "<=",  clickedDataset.date[1]]
                        ];
                        context = {
                            group_by: 'join_date',
                            search_default_join_date: `${2024}`
                        };
                        break;
                case areaName === 'Cimareme' && category === 'New Employee' :
                        domain = [
                            ["area", "=", 3],
                            ["emp_status", "in", ["probation", "confirmed"]],
                            "&",
                            ["join_date", ">=",  clickedDataset.date[0]], 
                            ["join_date", "<=",  clickedDataset.date[1]]
                        ];
                        context = {
                            group_by: 'join_date',
                            search_default_join_date: `${2024}`
                        };
                        break;
                case areaName === 'Cimahi' && category === 'New Employee' :
                        domain = [
                            ["area", "=", 2],
                            ["emp_status", "in", ["probation", "confirmed"]],
                            "&",
                            ["join_date", ">=",  clickedDataset.date[0]], 
                            ["join_date", "<=",  clickedDataset.date[1]]

                        ];
                        context = {
                            group_by: 'join_date',
                            search_default_join_date: `${2024}`
                        };
                        break;
                        case areaName === 'Taman Sari' && category === "Employee Exit":
                            domain = [
                                ["area", "=", 1],
                                // ["&", 
                                //     ["resign_date", ">=", `${new Date().getFullYear()}-${String(new Date().getMonth() + 1).padStart(2, "0")}-01`],
                                //     ["resign_date", "<=", `${new Date().getFullYear()}-${String(new Date().getMonth() + 1).padStart(2, "0")}-31`]
                                // ],
                                ["state", "=", "approved"],
                                "&",
                                ["resign_confirm_date", ">=",  clickedDataset.date[0]], 
                                ["resign_confirm_date", "<=",  clickedDataset.date[1]]
                                
                            ];
                            context = {
                                group_by: 'resign_confirm_date'
                            };
                            break;
                        case areaName === 'Cimareme' && category === "Employee Exit":
                            domain = [
                                ["area", "=", 3],
                                // ["&", 
                                //     ["resign_date", ">=", `${new Date().getFullYear()}-${String(new Date().getMonth() + 1).padStart(2, "0")}-01`],
                                //     ["resign_date", "<=", `${new Date().getFullYear()}-${String(new Date().getMonth() + 1).padStart(2, "0")}-31`]
                                // ],
                                ["state", "=", "approved"],
                                "&",
                                ["resign_confirm_date", ">=",  clickedDataset.date[0]], 
                                ["resign_confirm_date", "<=",  clickedDataset.date[1]]
                            ];
                            context = {
                                group_by: 'resign_confirm_date'
                            };
                            break;
                        case areaName === 'Cimahi' && category === "Employee Exit":
                            domain = [
                                ["area", "=", 2], 
                                
                                ["state", "=", "approved"],
                                "&",
                                ["resign_confirm_date", ">=",  clickedDataset.date[0]], 
                                ["resign_confirm_date", "<=",  clickedDataset.date[1]]
                            ];
                            context = {
                                group_by: 'resign_confirm_date'
                            };
                            break;
                case areaName === 'Taman Sari' && category === "Resign" :
                            domain = [
                                ["area", "=", 1],
                                ["resignation_type", "=", "RESG"],
                                ["state", "=", "approved"],
                                "&",
                                ["resign_confirm_date", ">=",  clickedDataset.date[0]], 
                                ["resign_confirm_date", "<=",  clickedDataset.date[1]]
                            ];
                            break;
                case areaName === 'Cimareme' && category === "Resign" :
                            domain = [
                                ["area", "=", 3],
                                ["resignation_type", "=", "RESG"],
                                ["state", "=", "approved"],
                                "&",
                                ["resign_confirm_date", ">=",  clickedDataset.date[0]], 
                                ["resign_confirm_date", "<=",  clickedDataset.date[1]]
                            ];
                            break;
                case areaName === 'Cimahi' && category === "Resign" :
                            domain = [
                                ["area", "=", 2],
                                // ["&", ("join_date", ">=", "2024-11-01"), ("join_date", "<=", "2024-11-30")]
                                ["resignation_type", "=", "RESG"],
                                ["state", "=", "approved"],
                                "&",
                                ["resign_confirm_date", ">=",  clickedDataset.date[0]], 
                                ["resign_confirm_date", "<=",  clickedDataset.date[1]]
                                // "&",
                                // ["resign_confirm_date", ">=", "2024-05-01"], 
                                // ["resign_confirm_date", "<=", "2024-11-26"]
                            ];
                            break;
                case areaName === 'Taman Sari' && category === "End Of Contract" :
                                domain = [
                                    ["area", "=", 1],
                                    ["resignation_type", "=", "EOCT"],
                                    ["state", "=", "approved"],
                                    "&",
                                ["resign_confirm_date", ">=",  clickedDataset.date[0]], 
                                ["resign_confirm_date", "<=",  clickedDataset.date[1]]
                                ];
                                break;
                case areaName === 'Cimareme' && category === "End Of Contract" :
                                domain = [
                                    ["area", "=", 3],
                                    ["resignation_type", "=", "EOCT"],
                                    ["state", "=", "approved"],
                                    "&",
                                ["resign_confirm_date", ">=",  clickedDataset.date[0]], 
                                ["resign_confirm_date", "<=",  clickedDataset.date[1]]
                                ];
                                break;
                case areaName === 'Cimahi' && category === "End Of Contract" :
                                domain = [
                                    ["area", "=", 2],
                                    // ["&", ("join_date", ">=", "2024-11-01"), ("join_date", "<=", "2024-11-30")]
                                    ["resignation_type", "=", "EOCT"],
                                    ["state", "=", "approved"],
                                    "&",
                                ["resign_confirm_date", ">=",  clickedDataset.date[0]], 
                                ["resign_confirm_date", "<=",  clickedDataset.date[1]]
                                ];
                                break;
                case areaName === 'Taman Sari' && category === "Transfer To Group" :
                                    domain = [
                                        ["area", "=", 1],
                                        ["resignation_type", "=", "TFTG"],
                                        ["state", "=", "approved"],
                                        "&",
                                ["resign_confirm_date", ">=",  clickedDataset.date[0]], 
                                ["resign_confirm_date", "<=",  clickedDataset.date[1]]
                                    ];
                                    break;
                case areaName === 'Cimareme' && category === "Transfer To Group" :
                                    domain = [
                                        ["area", "=", 3],
                                        ["resignation_type", "=", "TFTG"],
                                        ["state", "=", "approved"],
                                        "&",
                                ["resign_confirm_date", ">=",  clickedDataset.date[0]], 
                                ["resign_confirm_date", "<=",  clickedDataset.date[1]]
                                    ];
                                    break;
                case areaName === 'Cimahi' && category === "Transfer To Group" :
                                    domain = [
                                        ["area", "=", 2],
                                        // ["&", ("join_date", ">=", "2024-11-01"), ("join_date", "<=", "2024-11-30")]
                                        ["resignation_type", "=", "TFTG"],
                                        ["state", "=", "approved"],
                                        "&",
                                ["resign_confirm_date", ">=",  clickedDataset.date[0]], 
                                ["resign_confirm_date", "<=",  clickedDataset.date[1]]
                                    ];
                                    break;
                case areaName === 'Taman Sari' && category === "Terminate" :
                                        domain = [
                                            ["area", "=", 1],
                                            ["resignation_type", "=", "TERM"],
                                            ["state", "=", "approved"],
                                            "&",
                                ["resign_confirm_date", ">=",  clickedDataset.date[0]], 
                                ["resign_confirm_date", "<=",  clickedDataset.date[1]]
                                        ];
                                        break;
                case areaName === 'Cimareme' && category === "Terminate" :
                                        domain = [
                                            ["area", "=", 3],
                                            ["resignation_type", "=", "TERM"],
                                            ["state", "=", "approved"],
                                            "&",
                                ["resign_confirm_date", ">=",  clickedDataset.date[0]], 
                                ["resign_confirm_date", "<=",  clickedDataset.date[1]]
                                        ];
                                        break;
                case areaName === 'Cimahi' && category === "Terminate" :
                                        domain = [
                                            ["area", "=", 2],
                                            // ["&", ("join_date", ">=", "2024-11-01"), ("join_date", "<=", "2024-11-30")]
                                            ["resignation_type",  "=", "TERM"],
                                            ["state", "=", "approved"],
                                            "&",
                                ["resign_confirm_date", ">=",  clickedDataset.date[0]], 
                                ["resign_confirm_date", "<=",  clickedDataset.date[1]]
                                        ];
                                        break;
                case areaName === 'Taman Sari' && category === "Pension" :
                                            domain = [
                                                ["area", "=", 1],
                                                ["resignation_type",  "=", "RETR"],
                                                ["state", "=", "approved"],
                                                "&",
                                ["resign_confirm_date", ">=",  clickedDataset.date[0]], 
                                ["resign_confirm_date", "<=",  clickedDataset.date[1]]
                                            ];
                                            break;
                case areaName === 'Cimareme' && category === "Pension" :
                                            domain = [
                                                ["area", "=", 3],
                                                ["resignation_type",  "=", "RETR"],
                                                ["state", "=", "approved"],
                                                "&",
                                ["resign_confirm_date", ">=",  clickedDataset.date[0]], 
                                ["resign_confirm_date", "<=",  clickedDataset.date[1]]
                                            ];
                                            break;
                case areaName === 'Cimahi' && category === "Pension" :
                                            domain = [
                                                ["area", "=", 2],
                                                // ["&", ("join_date", ">=", "2024-11-01"), ("join_date", "<=", "2024-11-30")]
                                                ["resignation_type", "=", "RETR"],
                                                ["state", "=", "approved"],
                                                "&",
                                ["resign_confirm_date", ">=",  clickedDataset.date[0]], 
                                ["resign_confirm_date", "<=",  clickedDataset.date[1]]
                                            ];
                                            break;
            }
            if (domain.some(condition => condition[0] === "emp_status")) {
                // Buka view untuk `hr.employee`
                this.env.services.action.doAction({
                    type: 'ir.actions.act_window',
                    name: 'Employees',
                    res_model: 'hr.employee',
                    view_mode: 'tree',
                    view_id: 'hr.view_employee_tree',
                    views: [[false, 'tree']],
                    domain: domain,
                    context: context,
                    target: 'current'
                });
            } else if (domain.some(condition => condition[0] === "resignation_type" || condition[0] === "resign_confirm_date")) {
                // Buka view untuk `hr.resignation`
                this.env.services.action.doAction({
                    type: 'ir.actions.act_window',
                    name: 'HR Resignation',
                    res_model: 'hr.resignation',
                    view_mode: 'tree',
                    view_id: 'hr_resignation.hr_resignation_view_tree',
                    views: [[false, 'tree']],
                    context:"{'group_by': 'resign_confirm_date'}",
                    domain: domain,
                    target: 'current'
                });
            } else {
                console.error("Domain tidak valid atau tidak sesuai dengan aturan.");
            }
        } else {
            console.error('No elements clicked or elements is not an array');
        }
    }
    
    
}



ChartRenderer.template = "sanbe_hr_dashboard.ChartRendererField";
ChartRenderer.props = {
    type: { type: String, optional: true },
    data: { type: Object, optional: true },
    title: { type: String, optional: true }
};

// Register the component in the action registry
registry.category("actions").add("chart_dashboard", ChartRenderer);
