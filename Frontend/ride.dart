class Ride {
  final String id;
  final String origin;
  final String destination;
  final String status;
  final String riderId;
  final String driverId;

  Ride({
    required this.id,
    required this.origin,
    required this.destination,
    required this.status,
    required this.riderId,
    required this.driverId,
  });

  factory Ride.fromJson(Map<String, dynamic> json) {
    return Ride(
      id: json['id'],
      origin: json['origin'],
      destination: json['destination'],
      status: json['status'],
      riderId: json['rider_id'],
      driverId: json['driver_id'],
    );
  }
}