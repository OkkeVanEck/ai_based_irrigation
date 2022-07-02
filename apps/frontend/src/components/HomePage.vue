<!--TODO: SCHEDULE FOR WATERING ALL KNOWN SIMULATIONS FOR THIS USER ON FRONT PAGE-->

<template>
    <h1>Irrigation Optimization</h1>
    <div class="container">
        <div class="row row-cols-lg-auto g-3">
            <div class="col-12">
                <button type="button" class="form-control btn btn-danger"
                        @click="this.$router.push({ name: 'Create simulation' })">
                    New
                </button>
            </div>
            <div class="col-3" v-for="(sim, i) in simulations" :key="i">
                <button type="button" class="form-control btn btn-primary" @click="openSimulation(sim.id)">
                    <img :src="require(`../assets/${sim.crop_type}.svg`)" :alt="sim.crop_type"
                         class="m-2" width="30" />
                </button>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    async created() {
        await axios.get('http://ict4d-irrigation.westeurope.cloudapp.azure.com:5555/get-simulations')
            .then(res => {
                this.simulations = res.data
                console.log(this.simulations);
            })
    },
    data() {
        return {
            simulations: []
        }
    },
    methods: {
        openSimulation(uid) {
            this.$router.push({ name: 'Irrigation schedule', params: { uid: uid } })
        }
    }
}
</script>
