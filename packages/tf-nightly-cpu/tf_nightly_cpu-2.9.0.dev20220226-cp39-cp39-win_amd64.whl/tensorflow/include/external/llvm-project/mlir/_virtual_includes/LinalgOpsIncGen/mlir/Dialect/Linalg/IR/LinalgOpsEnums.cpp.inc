/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* Enum Utility Definitions                                                   *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

namespace mlir {
namespace linalg {
::llvm::StringRef stringifyTypeFn(TypeFn val) {
  switch (val) {
    case TypeFn::cast: return "cast";
    case TypeFn::cast_unsigned: return "cast_unsigned";
  }
  return "";
}

::llvm::Optional<TypeFn> symbolizeTypeFn(::llvm::StringRef str) {
  return ::llvm::StringSwitch<::llvm::Optional<TypeFn>>(str)
      .Case("cast", TypeFn::cast)
      .Case("cast_unsigned", TypeFn::cast_unsigned)
      .Default(::llvm::None);
}
::llvm::Optional<TypeFn> symbolizeTypeFn(uint32_t value) {
  switch (value) {
  case 0: return TypeFn::cast;
  case 1: return TypeFn::cast_unsigned;
  default: return ::llvm::None;
  }
}

} // namespace linalg
} // namespace mlir

