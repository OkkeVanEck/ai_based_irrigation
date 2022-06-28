<template>
    <a type="button" class="btn-link" @click="this.$router.push({ name: 'Home' })">Back</a>

    <h1>New simulation</h1>

    <div class="container-fluid">
        <form class="text-start">
            <div class="mb-3">
                <label class="form-label" for="crop">Crop type</label>
                <div class="d-block row button-carousel overflow-scroll text-nowrap">
                    <div class="d-inline-block col-3 text-center" v-for="(crop, i) in crops" :key="i">
                        <input type="radio" class="btn-check" name="crop type" :id="crop"
                               v-model="form.crop_type" :value="crop" autocomplete="off">
                        <label class="btn btn-success" :for="crop">
                            <img :src="require(`../assets/${crop}.svg`)" :alt="crop" class="m-2" width="30"/>
                        </label>
                    </div>
                </div>
            </div>

            <div class="mb-3">
                <label class="form-label" for="crop">Crop stage</label>
                <div class="d-block row button-carousel overflow-scroll text-nowrap">
                    <div class="d-inline-block col-3" v-for="(stage, i) in stages" :key="i">
                        <input type="radio" class="btn-check" name="crop stage" :id="stage"
                               v-model="form.crop_stage" :value="i" autocomplete="off">
                        <label class="btn btn-success" :for="stage">
                            <img :src="require(`../assets/crop stages/${stage}.svg`)" :alt="stage" class="m2"
                                 width="45"/>
                        </label>
                    </div>
                </div>
            </div>

            <div class="mb-3">
                <label class="form-label" for="startDate">Start date</label>
                <input id="startDate" class="form-control" type="date" v-model="form.start_date">
            </div>

            <div class="mb-3">
                <label class="form-label" for="endDate">Estimated harvest date</label>
                <input id="endDate" class="form-control" type="date" v-model="form.end_date" disabled>
            </div>

            <label for="maxWater" class="form-label">Maximum water capacity</label>
            <div class="input-group mb-3">
                <input type="number" class="form-control" id="maxWater" aria-describedby="maxWater"
                       v-model="form.max_water">
                <span class="input-group-text" id="water-addon">Liters</span>
            </div>

            <label for="fieldSize" class="form-label">Field size</label>
            <div class="input-group mb-3">
                <input type="number" class="form-control" id="fieldSize" aria-describedby="fieldSize"
                       v-model="form.field_size">
                <span class="input-group-text" id="size-addon">m<sup>2</sup></span>
            </div>

            <div class="d-flex align-items-center">
                <button class="btn btn-primary me-2" type="submit" @click="create_simulation()"
                        :disabled="this.loading">
                    <span v-if="!this.hasChanged && this.$route.params.uid">View schedule</span>
                    <span v-else-if="this.hasChanged">Rerun simulation</span>
                    <span v-else>Run simulation</span>
                </button>
                <strong v-if="this.loadMsg">{{ this.loadMsg }}</strong>
                <div v-if="this.loading" class="spinner-border ms-auto" role="status" aria-hidden="true"></div>
            </div>
        </form>
    </div>
</template>

<script>
import axios from 'axios';
import moment from 'moment';

let defaultForm;

export default {
    name: 'NewSimulationForm',
    async created() {
        // Always reset form first
        defaultForm = {
                crop_type: null,
                crop_stage: null,
                start_date: null,
                end_date: null,
                field_size: 0,
                max_water: 0
            };
        this.form = {...defaultForm};

        if (this.$route.params.uid) {
            await axios.get(`http://localhost:5555/get-simulation/${this.$route.params.uid}`)
                .then(res => {
                    let sim = res.data;
                    this.form.crop_type = sim.crop_type;
                    this.form.crop_stage = sim.crop_stage;
                    this.form.start_date = moment(sim.start_date).toISOString().substring(0, 10);
                    this.form.end_date = moment(sim.end_date).toISOString().substring(0, 10);
                    this.form.max_water = sim.max_water;
                    this.form.field_size = sim.field_size;

                    defaultForm = {...this.form}
                });
        }
    },
    data() {
        return {
            crops: ['Maize', 'Tomato', 'DryBean', 'Potato'],
            stages: ['emergence', 'anthesis', 'max rooting depth', 'canopy senescence'],
            form: {...defaultForm},
            loadMsg: null,
            loading: false
        }
    },
    methods: {
        create_simulation() {
            this.loadMsg = "Running simulation...";
            this.loading = true;
            axios.post('http://localhost:5555/create-simulation', {
                crop_type: this.form.crop_type,
                crop_stage: this.form.crop_stage,
                start_date: moment(this.form.start_date).format('YYYY/MM/DD'),
                end_date: moment(this.form.end_date).format('YYYY/MM/DD'),
                max_water: this.form.max_water,
                field_size: this.form.field_size
            })
                .then(res => {
                    console.log(res)
                    this.$router.push({name: 'Irrigation schedule', params: {uid: res.data}})
                })
                .catch(() => {
                    this.loadMsg = "Something went wrong. Please try again";
                })
                .finally(() => {
                    this.loading = false;
                })
        },
        get_crop_harvest_time() {
            axios.get(`http://localhost:5555/get-crop-harvest/${this.form.crop_type}`)
                .then(res => {
                    console.log(res.data);
                    this.form.end_date = moment(this.form.start_date).add(res.data, 'days').toISOString().substring(0, 10);
                });
        }
    },
    computed: {
        hasChanged() {
            return this.$route.params.uid && Object.keys(this.form).some(field => this.form[field] !== defaultForm[field])
        }
    },
    watch: {
        form: {
            handler(v) {
                if (v.crop_type && v.start_date) this.get_crop_harvest_time();
            },
            deep: true
        }
    }
}
</script>

<style>
.btn-check:checked + label > img {
    transform: scale(1.25);
    opacity: 0.3;
    border: none;
}

.col-3 img {
    cursor: pointer;
    transition: transform 1s;
    object-fit: cover;
}

.col-3 label {
    overflow: hidden;
    position: relative;
}
</style>