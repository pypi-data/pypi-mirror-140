/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* AttrDef Definitions                                                        *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

#ifdef GET_ATTRDEF_LIST
#undef GET_ATTRDEF_LIST

::mlir::linalg::TypeFnAttr

#endif  // GET_ATTRDEF_LIST

#ifdef GET_ATTRDEF_CLASSES
#undef GET_ATTRDEF_CLASSES

static ::mlir::OptionalParseResult generatedAttributeParser(::mlir::AsmParser &parser, ::llvm::StringRef mnemonic, ::mlir::Type type, ::mlir::Attribute &value) {
  if (mnemonic == ::mlir::linalg::TypeFnAttr::getMnemonic()) {
    value = ::mlir::linalg::TypeFnAttr::parse(parser, type);
    return ::mlir::success(!!value);
  }
  return {};
}

static ::mlir::LogicalResult generatedAttributePrinter(::mlir::Attribute def, ::mlir::AsmPrinter &printer) {
  return ::llvm::TypeSwitch<::mlir::Attribute, ::mlir::LogicalResult>(def)    .Case<::mlir::linalg::TypeFnAttr>([&](auto t) {
      printer << ::mlir::linalg::TypeFnAttr::getMnemonic();
t.print(printer);
      return ::mlir::success();
    })
    .Default([](auto) { return ::mlir::failure(); });
}

namespace mlir {
namespace linalg {
namespace detail {
struct TypeFnAttrStorage : public ::mlir::AttributeStorage {
  using KeyTy = std::tuple<::mlir::linalg::TypeFn>;
  TypeFnAttrStorage(::mlir::linalg::TypeFn value) : ::mlir::AttributeStorage(), value(value) {}

  bool operator==(const KeyTy &tblgenKey) const {
    return (value == std::get<0>(tblgenKey));
  }

  static ::llvm::hash_code hashKey(const KeyTy &tblgenKey) {
    return ::llvm::hash_combine(std::get<0>(tblgenKey));
  }

  static TypeFnAttrStorage *construct(::mlir::AttributeStorageAllocator &allocator, const KeyTy &tblgenKey) {
    auto value = std::get<0>(tblgenKey);
    return new (allocator.allocate<TypeFnAttrStorage>()) TypeFnAttrStorage(value);
  }

  ::mlir::linalg::TypeFn value;
};
} // namespace detail
TypeFnAttr TypeFnAttr::get(::mlir::MLIRContext *context, ::mlir::linalg::TypeFn value) {
  return Base::get(context, value);
}

::mlir::Attribute TypeFnAttr::parse(::mlir::AsmParser &odsParser, ::mlir::Type odsType) {
  ::mlir::FailureOr<::mlir::linalg::TypeFn> _result_value;
  ::llvm::SMLoc odsLoc = odsParser.getCurrentLocation();
  (void) odsLoc;
  // Parse literal '<'
  if (odsParser.parseLess()) return {};

  // Parse variable 'value'
  _result_value = [&]() -> ::mlir::FailureOr<::mlir::linalg::TypeFn> {
      auto loc = odsParser.getCurrentLocation();
      ::llvm::StringRef enumKeyword;
      if (::mlir::failed(odsParser.parseKeyword(&enumKeyword)))
        return ::mlir::failure();
      auto maybeEnum = ::mlir::linalg::symbolizeTypeFn(enumKeyword);
      if (maybeEnum)
        return *maybeEnum;
      return {(::mlir::LogicalResult)odsParser.emitError(loc, "expected ::mlir::linalg::TypeFn to be one of: cast, cast_unsigned")};
    }();
  if (::mlir::failed(_result_value)) {
    odsParser.emitError(odsParser.getCurrentLocation(), "failed to parse TypeFnAttr parameter 'value' which is to be a `::mlir::linalg::TypeFn`");
    return {};
  }
  // Parse literal '>'
  if (odsParser.parseGreater()) return {};
  assert(::mlir::succeeded(_result_value));
  return TypeFnAttr::get(odsParser.getContext(),
      *_result_value);
}

void TypeFnAttr::print(::mlir::AsmPrinter &odsPrinter) const {
  odsPrinter << "<";
  odsPrinter << stringifyTypeFn(getValue());
  odsPrinter << ">";
}

::mlir::linalg::TypeFn TypeFnAttr::getValue() const {
  return getImpl()->value;
}

} // namespace linalg
} // namespace mlir
DEFINE_EXPLICIT_TYPE_ID(::mlir::linalg::TypeFnAttr)
namespace mlir {
namespace linalg {

/// Parse an attribute registered to this dialect.
::mlir::Attribute LinalgDialect::parseAttribute(::mlir::DialectAsmParser &parser,
                                      ::mlir::Type type) const {
  ::llvm::SMLoc typeLoc = parser.getCurrentLocation();
  ::llvm::StringRef attrTag;
  if (::mlir::failed(parser.parseKeyword(&attrTag)))
    return {};
  {
    ::mlir::Attribute attr;
    auto parseResult = generatedAttributeParser(parser, attrTag, type, attr);
    if (parseResult.hasValue())
      return attr;
  }
  parser.emitError(typeLoc) << "unknown attribute `"
      << attrTag << "` in dialect `" << getNamespace() << "`";
  return {};
}
/// Print an attribute registered to this dialect.
void LinalgDialect::printAttribute(::mlir::Attribute attr,
                         ::mlir::DialectAsmPrinter &printer) const {
  if (::mlir::succeeded(generatedAttributePrinter(attr, printer)))
    return;
}
} // namespace linalg
} // namespace mlir

#endif  // GET_ATTRDEF_CLASSES

