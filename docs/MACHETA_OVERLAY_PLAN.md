# 🗺️ Plan Implementare Machetă Overlay + Google Maps

## 📋 Concept

Combinare între:
- **Google Maps API** - pentru navigație GPS reală și directions
- **Machetă fizică** - overlay custom peste hartă pentru vizualizare realistă

## 🎯 Obiective

1. ✅ GPS navigation funcționează real (calculează ruta de la poziția utilizatorului la spot)
2. ✅ Vizualizare machetă fizică (nu vezi harta Google Maps standard)
3. ✅ Demo perfect în clasă (nu apare New York când ești în România)
4. ✅ Sincronizare 1:1 între machetă fizică și spots digitale

## 🛠️ Implementare Tehnică

### Pas 1: Pregătire Machetă

**Ce trebuie:**
- Poză top-down a machetei (PNG transparent preferabil)
- Dimensiuni: 1920x1080px sau mai mare
- Format: PNG cu transparență sau JPG

**Plasare:**
```
apps/mobile/assets/images/parking_lot_overlay.png
```

**Actualizare pubspec.yaml:**
```yaml
flutter:
  assets:
    - assets/images/parking_lot_overlay.png
```

### Pas 2: Coordonate GPS Machetă

**Definire colțuri:**
```dart
// Colț stânga-sus al machetei
final LatLng topLeft = LatLng(44.4268, 26.1025); 

// Colț dreapta-jos al machetei  
final LatLng bottomRight = LatLng(44.4265, 26.1030);
```

**Calibrare:**
- Pune macheta fizică pe o hartă Google Maps
- Notează coordonatele GPS ale colțurilor
- Folosește Google Maps web pentru precizie

### Pas 3: Overlay Implementation

**Structură Stack:**
```dart
Stack(
  children: [
    // 1. Google Maps (invizibil sau semi-transparent)
    GoogleMap(
      initialCameraPosition: CameraPosition(
        target: center, // Centrul machetei
        zoom: 19.0,
      ),
      mapType: MapType.none, // ASCUNDE HARTA
      myLocationEnabled: true,
      markers: _markers,
    ),
    
    // 2. Overlay machetă
    Positioned.fill(
      child: GroundOverlay(
        imageAsset: 'assets/images/parking_lot_overlay.png',
        bounds: LatLngBounds(
          southwest: bottomRight,
          northeast: topLeft,
        ),
        transparency: 0.0, // Opac complet
      ),
    ),
    
    // 3. Spots interactive
    ...buildSpotMarkers(),
    
    // 4. User position indicator
    StreamBuilder<Position>(
      stream: Geolocator.getPositionStream(),
      builder: (context, snapshot) {
        return CustomPositionIndicator(
          position: snapshot.data,
          machetaBounds: bounds,
        );
      },
    ),
  ],
)
```

### Pas 4: Conversie Coordonate GPS → Poziție Machetă

**Formula:**
```dart
Offset gpsToMachetaPosition(LatLng gpsPosition, Size machetaSize) {
  // Normalizare GPS între 0-1
  final latRange = topLeft.latitude - bottomRight.latitude;
  final lngRange = bottomRight.longitude - topLeft.longitude;
  
  final normalizedLat = (topLeft.latitude - gpsPosition.latitude) / latRange;
  final normalizedLng = (gpsPosition.longitude - topLeft.longitude) / lngRange;
  
  // Mapare la dimensiuni machetă
  return Offset(
    normalizedLng * machetaSize.width,
    normalizedLat * machetaSize.height,
  );
}
```

### Pas 5: Directions & Navigation

**Google Directions API:**
```dart
Future<List<LatLng>> getDirections(LatLng from, LatLng to) async {
  final url = 'https://maps.googleapis.com/maps/api/directions/json'
      '?origin=${from.latitude},${from.longitude}'
      '&destination=${to.latitude},${to.longitude}'
      '&key=$GOOGLE_MAPS_API_KEY';
  
  final response = await http.get(Uri.parse(url));
  final data = json.decode(response.body);
  
  // Parse polyline și returnează listă LatLng
  return decodePolyline(data['routes'][0]['overview_polyline']['points']);
}
```

**Afișare rută pe machetă:**
```dart
CustomPaint(
  painter: RoutePainter(
    routePoints: _routePoints.map((gps) => 
      gpsToMachetaPosition(gps, machetaSize)
    ).toList(),
    color: Colors.blue.withOpacity(0.8),
  ),
)
```

## 📊 Structură Fișiere Actualizate

```
apps/mobile/lib/
├── screens/
│   ├── maps/
│   │   ├── parking_map_screen.dart (UPDATE)
│   │   ├── macheta_overlay_widget.dart (NOU)
│   │   └── gps_to_macheta_converter.dart (NOU)
│   └── navigation/
│       └── directional_navigation_screen.dart (UPDATE)
└── services/
    └── google_directions_service.dart (NOU)

apps/mobile/assets/
└── images/
    └── parking_lot_overlay.png (VIITOR)
```

## 🔧 Configurare Backend

**Schema Update (prisma/schema.prisma):**
```prisma
model ParkingConfig {
  id          Int      @id @default(autoincrement())
  
  // Existing
  entranceLat Float
  entranceLng Float
  exitLat     Float
  exitLng     Float
  shopLat     Float
  shopLng     Float
  
  // NEW: Macheta bounds
  machetaTopLeftLat     Float?
  machetaTopLeftLng     Float?
  machetaBottomRightLat Float?
  machetaBottomRightLng Float?
  machetaOverlayUrl     String? // Pentru versiune web
  
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
}
```

**Migration:**
```bash
cd apps/api
npx prisma migrate dev --name add_macheta_config
```

## 📱 UI/UX Features

### Admin Config Screen
- [ ] Upload poză machetă
- [ ] Drag corners pentru calibrare GPS
- [ ] Preview overlay peste Google Maps
- [ ] Save macheta bounds în DB

### User Map Screen  
- [ ] Toggle între "Macheta View" și "Google Maps View"
- [ ] Zoom/pan pe machetă
- [ ] Tap spot pentru detalii
- [ ] Real-time GPS position pe machetă

### Navigation Screen
- [ ] Arrow direction bazat pe GPS real
- [ ] Distance calculation (Haversine)
- [ ] "Turn by turn" overlay pe machetă
- [ ] Voice navigation (opțional)

## 🚀 Faze Implementare

### Faza 1: Setup (1-2 ore)
- [x] Documentație plan
- [ ] Add macheta fields în ParkingConfig schema
- [ ] Migration database
- [ ] Update API endpoints

### Faza 2: Macheta Upload (2-3 ore)
- [ ] File picker în admin config
- [ ] Upload to server/cloud storage
- [ ] Save URL în database
- [ ] Display în app

### Faza 3: GPS Calibration (2-3 ore)
- [ ] Draggable corners pe hartă
- [ ] Save bounds coordinates
- [ ] Test conversion GPS → Pixel

### Faza 4: Overlay Integration (3-4 ore)
- [ ] GroundOverlay widget
- [ ] Stack configuration
- [ ] Spot markers overlay
- [ ] User position indicator

### Faza 5: Directions API (2-3 ore)
- [ ] Google Directions service
- [ ] Polyline decoding
- [ ] Route painter pe machetă
- [ ] Real-time updates

### Faza 6: Testing & Polish (2-3 ore)
- [ ] Test calibrare precizie
- [ ] Performance optimization
- [ ] Error handling
- [ ] UI polish

**Total estimat: 12-18 ore**

## 📌 Note Importante

### Google Maps API Key
```
Trebuie activat:
- Maps SDK for iOS
- Maps SDK for Android  
- Directions API
- Geocoding API
```

### Billing Google Cloud
- Directions API: $5 per 1000 requests
- Static Maps API: $2 per 1000 requests
- Recomandat: Set billing alerts

### Alternative Fără Cost
- Mapbox (free tier mai generos)
- OpenStreetMap + OSRM (complet gratis)
- Custom routing algorithm (pentru demo)

## 🎓 Demo în Clasă

**Scenarii demonstrație:**

1. **Setup inițial:**
   - Admin uploadează poză machetă
   - Calibrare colțuri GPS
   - Plasare spots pe machetă

2. **User flow:**
   - Login user
   - Vezi macheta cu spots disponibile
   - Scanează QR la intrare
   - Smart allocation → spot assigned
   - Navigate: GPS real → arrow pe machetă
   - Găsește spotul pe macheta fizică

3. **BYPASS Mode:**
   - Simulare car detection
   - Update real-time pe machetă
   - Spot devine ocupat (roșu)

## 📚 Resurse

- [Google Maps Overlay](https://developers.google.com/maps/documentation/android-sdk/groundoverlay)
- [Directions API](https://developers.google.com/maps/documentation/directions/overview)
- [Flutter Google Maps Plugin](https://pub.dev/packages/google_maps_flutter)
- [Coordinate Conversion](https://stackoverflow.com/questions/14329691/convert-latitude-longitude-point-to-a-pixels-x-y-on-mercator-projection)

---

**Status:** 📋 PLANIFICAT - Ready pentru implementare când macheta fizică este gata!

**Contact:** Întreabă când ești ready să implementezi! 🚀
