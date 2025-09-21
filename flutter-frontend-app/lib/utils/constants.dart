class DataTypes {
  static const String string = 'string';
  static const String integer = 'integer';
  static const String decimal = 'decimal';
  static const String datetime = 'datetime';

  static List<String> get all => [string, integer, decimal, datetime];
}

class ApiEndpoints {
  static const String baseUrl = 'http://localhost:5000';
  static const String process = '/process';
  static const String load = '/load';
}
