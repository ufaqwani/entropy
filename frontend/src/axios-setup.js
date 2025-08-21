import axios from 'axios';

// Point ALL axios calls to your backend URL from Netlify env
axios.defaults.baseURL = process.env.REACT_APP_API_BASE_URL;

// If you use cookies/sessions, keep credentials
axios.defaults.withCredentials = true;

// Optional: simple error logging in dev
if (process.env.NODE_ENV !== 'production') {
  axios.interceptors.response.use(
    r => r,
    e => {
      // eslint-disable-next-line no-console
      console.error('[axios]', e?.response?.status, e?.response?.data || e?.message);
      return Promise.reject(e);
    }
  );
}
