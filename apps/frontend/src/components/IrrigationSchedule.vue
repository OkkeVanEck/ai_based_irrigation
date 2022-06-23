<template>
    <a type="button" class="btn-link" @click="this.$router.push({ name: 'Create simulation' })">Settings</a> |
    <a type="button" class="btn-link" @click="this.$router.push({ name: 'Home' })">Home</a>

    <h1>Irrigation Schedule</h1>

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
                this.calendar_from_date = new Date(this.simulation.start_date)

                this.attributes = [{
                    key: 0,
                    highlight: true,
                    dot: false,
                    bar: false,
                    content: 'blue',
                    popover: {
                        label: '4 Liters',
                    },
                    // customData: {...},
                    dates: new Date(2021, 9,21),
                    excludeDates: null,
                    order: 0
                }];

                console.log(this.simulation);
            })
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
