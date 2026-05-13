// frontend/src/features/ops/api/opsApi.js

import api from '../../../lib/axios'

// ── Bookings ──────────────────────────────────────────────────────────────────
export const fetchOpsBookings = (params = {}) =>
  api.get('/ops/bookings/', { params }).then(r => r.data) // uses ops-list from Phase 6

export const fetchBookingDetail = (id) =>
  api.get(`/bookings/${id}/`).then(r => r.data)

export const updateBookingStatus = (id, payload) =>
  api.patch(`/bookings/ops/${id}/status/`, payload).then(r => r.data)

// ── Crew ──────────────────────────────────────────────────────────────────────
export const fetchMovers = () =>
  api.get('/ops/movers/').then(r => r.data)

export const fetchBookingCrew = (bookingId) =>
  api.get(`/ops/bookings/${bookingId}/crew/`).then(r => r.data)

export const assignCrew = (bookingId, payload) =>
  api.post(`/ops/bookings/${bookingId}/crew/assign/`, payload).then(r => r.data)

export const unassignMover = (bookingId, payload) =>
  api.delete(`/ops/bookings/${bookingId}/crew/unassign/`, { data: payload }).then(r => r.data)

// ── Schedule ──────────────────────────────────────────────────────────────────
export const fetchDailySchedule = (date) =>
  api.get('/ops/schedule/daily/', { params: { date } }).then(r => r.data)

export const fetchWeeklySchedule = (startDate) =>
  api.get('/ops/schedule/weekly/', { params: { start_date: startDate } }).then(r => r.data)

// ── Analytics ─────────────────────────────────────────────────────────────────
export const fetchAnalyticsOverview = (params) =>
  api.get('/ops/analytics/overview/', { params }).then(r => r.data)

export const fetchDailyRevenue = (params) =>
  api.get('/ops/analytics/revenue/daily/', { params }).then(r => r.data)

export const fetchBookingVolumes = (params) =>
  api.get('/ops/analytics/bookings/daily/', { params }).then(r => r.data)

export const fetchHouseSizeBreakdown = (params) =>
  api.get('/ops/analytics/house-sizes/', { params }).then(r => r.data)