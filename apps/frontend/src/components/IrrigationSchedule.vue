<template>
    <a type="button" class="btn-link" @click="this.$router.push({name: 'Create simulation', params: {uid: this.simulation.id}})">
        Settings
    </a> |
    <a type="button" class="btn-link" @click="this.$router.push({ name: 'Home' })">Home</a>

    <h1>Irrigation Schedule</h1>
    <div>{{this.simulation.crop_type}}</div>

    <div class="container">
        <Calendar :columns="layout.columns"
                  :rows="layout.rows"
                  :is-expanded="layout.isExpanded"
                  :attributes="attributes"
                  :from-date="this.calendar_from_date"/>
    </div>
</template>

<script>
import axios from "axios";

export default {
    name: 'IrrigationSchedule',
    async created() {
        await axios.get(`http://localhost:5555/get-simulation/${this.$route.params.uid}`)
            .then(res => {
                this.simulation = res.data;
                console.log(this.simulation);

                this.calendar_from_date = new Date(this.simulation.start_date);

                this.attributes = [];

                // Add watering dates to calendar
                Object.entries(this.simulation.schedule).forEach(([date, liters]) => {
                    if (liters > 0) {
                        this.attributes.push({
                            key: 0,
                            highlight: 'blue',
                            dot: false,
                            bar: false,
                            popover: {
                                label: `${liters} Liters`,
                            },
                            // customData: {...},
                            dates: Date.parse(date),
                            excludeDates: null,
                            order: 0
                        });
                    }
                });

                // Add harvest date to calendar
                if (this.simulation.harvest_date !== 'undefined') {
                    this.attributes.push({
                        key: 0,
                        highlight: 'green',
                        dot: false,
                        bar: false,
                        popover: {
                            label: `Expected optimal harvest date`,
                        },
                        // customData: {...},
                        dates: new Date(this.simulation.harvest_date),
                        excludeDates: null,
                        order: 0
                    });
                }
            });
    },
    computed: {
        layout() {
            return this.$screens(
                {
                    // Default layout for mobile
                    default: {
                        columns: 1,
                        rows: 2,
                        isExpanded: true,
                    },
                    // Override for large screens
                    lg: {
                        columns: 2,
                        rows: 2,
                        isExpanded: false,
                    },
                },
            );
        }
    },
    data() {
        return {
            calendar_from_date: new Date(),
            attributes: [],
            simulation: null
        };
    }
}
</script>
