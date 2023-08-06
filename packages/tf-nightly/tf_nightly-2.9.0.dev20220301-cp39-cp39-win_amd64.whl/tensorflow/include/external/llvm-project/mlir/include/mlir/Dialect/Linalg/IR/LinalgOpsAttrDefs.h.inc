/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* AttrDef Declarations                                                       *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

#ifdef GET_ATTRDEF_CLASSES
#undef GET_ATTRDEF_CLASSES


namespace mlir {
class AsmParser;
class AsmPrinter;
} // namespace mlir
namespace mlir {
namespace linalg {
class TypeFnAttr;
namespace detail {
struct TypeFnAttrStorage;
} // namespace detail
class TypeFnAttr : public ::mlir::Attribute::AttrBase<TypeFnAttr, ::mlir::Attribute, detail::TypeFnAttrStorage> {
public:
  using Base::Base;
  static TypeFnAttr get(::mlir::MLIRContext *context, ::mlir::linalg::TypeFn value);
  static constexpr ::llvm::StringLiteral getMnemonic() {
    return {"type_fn"};
  }

  static ::mlir::Attribute parse(::mlir::AsmParser &odsParser, ::mlir::Type odsType);
  void print(::mlir::AsmPrinter &odsPrinter) const;
  ::mlir::linalg::TypeFn getValue() const;
};
} // namespace linalg
} // namespace mlir
DECLARE_EXPLICIT_TYPE_ID(::mlir::linalg::TypeFnAttr)

#endif  // GET_ATTRDEF_CLASSES

