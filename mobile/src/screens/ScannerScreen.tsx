import React, { useState } from 'react';
import { StyleSheet, Text, View, TextInput, TouchableOpacity, Alert, Linking } from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { useSyncStore } from '../store/useSyncStore';

export function ScannerScreen() {
  const [permission, requestPermission] = useCameraPermissions();
  const [scannedUrl, setScannedUrl] = useState<string | null>(null);
  
  const [name, setName] = useState('');
  const [cpf, setCpf] = useState('');
  const [plate, setPlate] = useState('');

  const addHandshake = useSyncStore(state => state.addHandshake);

  if (!permission) {
    return <View style={styles.container} />;
  }

  if (!permission.granted) {
    return (
      <View style={styles.container}>
        <Text style={styles.message}>Precisamos da sua permissão para usar a câmera e escanear o QR Code da carga.</Text>
        <TouchableOpacity style={styles.primaryButton} onPress={requestPermission}>
          <Text style={styles.primaryButtonText}>Permitir Câmera</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.secondaryButton} onPress={() => Linking.openSettings()}>
          <Text style={styles.secondaryButtonText}>Abrir Configurações</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const handleBarcodeScanned = ({ type, data }: { type: string; data: string }) => {
    if (scannedUrl) return; 
    setScannedUrl(data);
  };

  const handleSubmit = () => {
    if (!name || !cpf || !plate) {
      Alert.alert('Atenção', 'Por favor, preencha todos os campos para assumir a carga.');
      return;
    }

    addHandshake(scannedUrl!, {
      driver_name: name,
      driver_cpf: cpf,
      vehicle_plate: plate,
    });

    Alert.alert(
      'Carga Recebida!',
      'Informações salvas. Os dados serão enviados automaticamente quando houver sinal de internet.',
      [
        {
          text: 'OK',
          onPress: () => {
            setScannedUrl(null);
            setName('');
            setCpf('');
            setPlate('');
          }
        }
      ]
    );
  };

  return (
    <View style={styles.container}>
      {!scannedUrl ? (
        <View style={styles.cameraContainer}>
          <CameraView 
            style={StyleSheet.absoluteFillObject} 
            facing="back"
            onBarcodeScanned={scannedUrl ? undefined : handleBarcodeScanned}
          />
          <View style={styles.overlay}>
            <Text style={styles.overlayText}>Aponte a câmera para o QR Code da carga</Text>
            <View style={styles.scanBox} />
          </View>
        </View>
      ) : (
        <View style={styles.formContainer}>
          <Text style={styles.formTitle}>Identificação</Text>
          <Text style={styles.formSubtitle}>Carga identificada. Por favor, preencha os dados abaixo para continuar.</Text>
          
          <TextInput
            style={styles.input}
            placeholder="Nome Completo (ex: João da Silva)"
            value={name}
            onChangeText={setName}
            autoCapitalize="words"
            placeholderTextColor="#9ca3af"
          />
          
          <TextInput
            style={styles.input}
            placeholder="CPF (apenas números)"
            value={cpf}
            onChangeText={setCpf}
            keyboardType="number-pad"
            placeholderTextColor="#9ca3af"
          />
          
          <TextInput
            style={styles.input}
            placeholder="Placa do Caminhão (ex: ABC1234)"
            value={plate}
            onChangeText={setPlate}
            autoCapitalize="characters"
            placeholderTextColor="#9ca3af"
          />

          <TouchableOpacity style={styles.primaryButtonForm} onPress={handleSubmit}>
            <Text style={styles.primaryButtonText}>Receber Carga</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.cancelButton} onPress={() => setScannedUrl(null)}>
            <Text style={styles.cancelButtonText}>Cancelar Leitura</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    backgroundColor: '#18181b', 
  },
  message: {
    textAlign: 'center',
    paddingBottom: 24,
    fontSize: 18,
    color: '#f4f4f5',
    paddingHorizontal: 20,
    lineHeight: 28,
  },
  cameraContainer: {
    flex: 1,
  },
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.6)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  overlayText: {
    color: '#fff',
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 40,
    textAlign: 'center',
    textShadowColor: 'rgba(0, 0, 0, 0.9)',
    textShadowOffset: { width: -1, height: 1 },
    textShadowRadius: 10
  },
  scanBox: {
    width: 260,
    height: 260,
    borderWidth: 4,
    borderColor: '#3b82f6',
    backgroundColor: 'transparent',
    borderRadius: 16,
  },
  formContainer: {
    flex: 1,
    padding: 24,
    justifyContent: 'center',
    backgroundColor: '#ffffff',
  },
  formTitle: {
    fontSize: 34,
    fontWeight: '900',
    color: '#111827',
    marginBottom: 8,
  },
  formSubtitle: {
    fontSize: 16,
    color: '#4b5563',
    marginBottom: 32,
    lineHeight: 24,
  },
  input: {
    height: 70, 
    borderWidth: 2,
    borderColor: '#e5e7eb',
    borderRadius: 12,
    marginBottom: 16,
    paddingHorizontal: 20,
    fontSize: 20, 
    backgroundColor: '#f9fafb',
    color: '#111827',
  },
  primaryButton: {
    height: 64,
    backgroundColor: '#2563eb',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: 20,
  },
  primaryButtonForm: {
    height: 70,
    backgroundColor: '#2563eb',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 16,
    shadowColor: '#2563eb',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
  },
  primaryButtonText: {
    color: 'white',
    fontSize: 22,
    fontWeight: '900',
  },
  secondaryButton: {
    height: 64,
    backgroundColor: '#3f3f46',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 16,
    marginHorizontal: 20,
  },
  secondaryButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  cancelButton: {
    height: 64,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 12,
  },
  cancelButtonText: {
    color: '#dc2626',
    fontSize: 18,
    fontWeight: 'bold',
  }
});
