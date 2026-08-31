import axios from 'axios';
import { Platform } from 'react-native';

// Trata o localhost no Android Emulator dinamicamente
const baseURL = Platform.OS === 'android' ? 'http://10.0.2.2:8000/api' : 'http://localhost:8000/api';

export const api = axios.create({
  baseURL,
});
