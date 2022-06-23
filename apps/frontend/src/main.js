import { createApp } from 'vue'
import { SetupCalendar, Calendar, DatePicker } from 'v-calendar';
import 'bootstrap'
import 'bootstrap/dist/css/bootstrap.min.css'

import {createRouter, createWebHistory} from 'vue-router'
import App from './App.vue'
import Home from './components/HomePage.vue';
import NewSimulationForm from './components/NewSimulationForm.vue';
import IrrigationSchedule from "@/components/IrrigationSchedule";

const routes = [
    {
        path: '/',
        name: 'Home',
        component: Home
    },
    {
        path: '/new',
        name: 'Create simulation',
        component: NewSimulationForm
    },
    {
        path: '/schedule/:uid',
        name: 'Irrigation schedule',
        component: IrrigationSchedule
    },
];

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes
});

const app = createApp(App)

app.use(SetupCalendar, {})
app.use(router)

app.component('Calendar', Calendar)
app.component('DatePicker', DatePicker)

app.mount('#app')
