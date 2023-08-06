/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* Enum Utility Declarations                                                  *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

namespace mlir {
namespace linalg {
// allowed 32-bit signless integer cases: 0, 1
enum class TypeFn : uint32_t {
  cast = 0,
  cast_unsigned = 1,
};

::llvm::Optional<TypeFn> symbolizeTypeFn(uint32_t);
::llvm::StringRef stringifyTypeFn(TypeFn);
::llvm::Optional<TypeFn> symbolizeTypeFn(::llvm::StringRef);
inline constexpr unsigned getMaxEnumValForTypeFn() {
  return 1;
}


inline ::llvm::StringRef stringifyEnum(TypeFn enumValue) {
  return stringifyTypeFn(enumValue);
}

template <typename EnumType>
::llvm::Optional<EnumType> symbolizeEnum(::llvm::StringRef);

template <>
inline ::llvm::Optional<TypeFn> symbolizeEnum<TypeFn>(::llvm::StringRef str) {
  return symbolizeTypeFn(str);
}
} // namespace linalg
} // namespace mlir

namespace llvm {
template<> struct DenseMapInfo<::mlir::linalg::TypeFn> {
  using StorageInfo = ::llvm::DenseMapInfo<uint32_t>;

  static inline ::mlir::linalg::TypeFn getEmptyKey() {
    return static_cast<::mlir::linalg::TypeFn>(StorageInfo::getEmptyKey());
  }

  static inline ::mlir::linalg::TypeFn getTombstoneKey() {
    return static_cast<::mlir::linalg::TypeFn>(StorageInfo::getTombstoneKey());
  }

  static unsigned getHashValue(const ::mlir::linalg::TypeFn &val) {
    return StorageInfo::getHashValue(static_cast<uint32_t>(val));
  }

  static bool isEqual(const ::mlir::linalg::TypeFn &lhs, const ::mlir::linalg::TypeFn &rhs) {
    return lhs == rhs;
  }
};
}

